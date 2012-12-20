from xml.dom import minidom
from celery import task, current_task
from apps.instance.models import Instance, InstanceTask
from apps.storagepool.models import StoragePool
from apps.volume.models import Volume
from django.contrib import messages
from django.http import HttpRequest
import persistent_messages
import libvirt

@task()
def create_instance(instancetask_name):
  try:
    instancetask = InstanceTask.objects.get(name=instancetask_name)
  except InstanceTask.DoesNotExist:
    return {'custum_state': 'FAILURE', 'msg': 'Unable to find InstanceTask with name: %s' % (instancetask_name)}

  request = HttpRequest()
  storagepool = instancetask.storagepool.get_storagepool()
  if not storagepool:
    return {'custom_state': 'FAILURE', 'msg': 'Unable to get Storage Pool %s' % (instancetask.storagepool)}

  volume_name = Volume.create_random_name()
  (volume, created) = Volume.objects.get_or_create(
    name=volume_name,
    storagepool=instancetask.storagepool,
    capacity=instancetask.capacity
  )
  if created: volume.save()
  if not volume.create(request):
    volume.delete()
    return {'custom_state': 'FAILURE', 'msg': 'Unable to create Volume on %s' % (instancetask.storagepool)}
  instancetask.volume = volume
  instancetask.save()

  installationdisk_path = ''
  if instancetask.disk:
    installationdisk_path = instancetask.disk.path()
  
  xml = """
    <domain type='kvm'>
        <name>%s</name>
        <memory unit="b">%d</memory>
        <currentMemory unit="b">%d</currentMemory>
        <vcpu>%s</vcpu>
        <os>
            <type arch='x86_64' machine='pc'>hvm</type>
            <boot dev='hd'/>
            <boot dev='cdrom'/>
            <bootmenu enable='yes'/>
        </os>
        <features>
            <acpi/>
            <apic/>
            <pae/>
        </features>
        <clock offset='utc'/>
            <on_poweroff>destroy</on_poweroff>
            <on_reboot>restart</on_reboot>
            <on_crash>restart</on_crash>
        <devices>
            <emulator>/usr/bin/kvm</emulator>
            <disk type='file' device='disk'>
                <driver name='qemu' type='qcow2'/>
                <source file='%s'/>
                <target dev='hda' bus='ide'/>
                <alias name='ide0-0-0'/>
                <address type='drive' controller='0' bus='0' target='0' unit='0'/>
            </disk>
            <disk type='file' device='cdrom'>
                <driver name='qemu' type='raw'/>
                <source file='%s'/>
                <target dev='hdc' bus='ide'/>
                <readonly/>
                <address type='drive' controller='0' bus='1' unit='0'/>
            </disk>
            <controller type='ide' index='0'>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
            </controller>
            <interface type='bridge'>
                <source bridge='br0' />
                <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
            </interface>
            <input type='tablet' bus='usb'/>
            <input type='mouse' bus='ps2'/>
            <graphics type='vnc' port='-1' autoport='yes'/>
            <video>
                <model type='cirrus' vram='9216' heads='1'/>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
            </video>
            <memballoon model='virtio'>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
          </memballoon>
      </devices>
  </domain>""" \
    % (instancetask.name, instancetask.memory, instancetask.memory, 
      instancetask.vcpu, volume.path(), installationdisk_path)
  print xml
  con = instancetask.storagepool.hypervisor.get_connection()
  if not con:
    return {'custom_state': 'FAILURE', 'msg': 'Unable to get Hypervisor %s' % (instancetask.storagepool.hypervisor)}
    
  try:
    con.defineXML(xml)
    current_task.update_state(state='PROGRESS', meta={
      'percent': 15,
      'msg': 'Defined XML'
    })
    instance = con.lookupByName(instancetask.name)
    instance.setAutostart(1)
    current_task.update_state(state='PROGRESS', meta={
      'percent': 50,
      'msg': 'Set Autostart',
    })
    instance.create()
    current_task.update_state(state='PROGRESS', meta={
      'percent': 75,
      'msg': 'Creating the Instance on the Hypervisor..',
    })
    # switch instance task for an instance
    new_instance = Instance.objects.create(
      name=instancetask.name,
      volume=instancetask.volume,
      user=instancetask.user,
      creator=instancetask.creator,
      vcpu=instancetask.vcpu,
      memory=instancetask.memory,
      disk=instancetask.disk,
      created=instancetask.created
    )
    new_instance.save()
    instancetask.delete(False)
  except libvirt.libvirtError as e:
    return {'custom_state': 'FAILURE', 'msg': 'Error while creating instance: %s' % (e)}

  
    
