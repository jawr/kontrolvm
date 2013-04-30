from xml.dom import minidom
from celery import task, current_task
from apps.instance.models import Instance, InstanceTask
from apps.network.models import NoUniqueAddress, InstanceNetwork
from apps.storagepool.models import StoragePool
from apps.volume.models import Volume
from django.contrib import messages
from django.http import HttpRequest
from xml.etree import ElementTree
import persistent_messages
import libvirt

@task()
def create_instance(instancetask_name):
  try:
    instancetask = InstanceTask.objects.get(name=instancetask_name)
  except InstanceTask.DoesNotExist:
    return {'custum_state': 'FAILURE', 'msg': 'Unable to find InstanceTask with name: %s' % (instancetask_name)}

  try:
    network_address = instancetask.network.create_unique_address()
  except NoUniqueAddress:
    return {'custum_state': 'FAILURE', 'msg': 'Error while creating instance: No unique address available on specified network (%s)' % (instancetask.network)}

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

  xml = """
    <domain type='kvm'>
        <name>%s</name>
        <memory unit="b">%d</memory>
        <currentMemory unit="b">%d</currentMemory>
        <vcpu>%s</vcpu>
        <os>
            <type arch='x86_64' machine='pc'>hvm</type>
            <boot dev='cdrom'/>
            <boot dev='hd'/>
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
            <disk type='file' device='cdrom'>
                <driver name='qemu' type='raw'/>
                <target dev='hdc' bus='ide'/>
            </disk>
            <disk type='file' device='disk'>
                <driver name='qemu' type='qcow2'/>
                <source file='%s'/>
                <target dev='hda' bus='virtio'/>
                <alias name='ide0-0-0'/>
            </disk>
            <controller type='ide' index='0'>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x01' function='0x1'/>
            </controller>
            <interface type='bridge'>
                <source bridge='br0' />
                <address type='pci' domain='0x0000' bus='0x00' slot='0x03' function='0x0'/>
                <filterref filter='clean-traffic'>
                  <parameter name='IP' value='%s' />
                </filterref>
                <model type='virtio'/>
            </interface>
            <input type='tablet' bus='usb'/>
            <input type='mouse' bus='ps2'/>
            <graphics type='vnc' port='-1' autoport='yes'>
              <listen type='address' address='%s' />
            </graphics>
            <video>
                <model type='cirrus' vram='9216' heads='1'/>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x02' function='0x0'/>
            </video>
            <memballoon model='virtio'>
                <address type='pci' domain='0x0000' bus='0x00' slot='0x05' function='0x0'/>
          </memballoon>
      </devices>
  </domain>""" \
    % (instancetask.name, instancetask.memory.size, instancetask.memory.size, 
      instancetask.vcpu, volume.path(), network_address.ip, volume.storagepool.hypervisor.address)
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

    # shutdown initially so that user can pick their own install medium
    instance.destroy()

    # get mac info and setup network
    tree = ElementTree.fromstring(instance.XMLDesc(0))
    address = tree.findall('devices/interface/mac')
    mac = address[0].get('address').upper()
    print "MAC: %s" % (mac)
    if Instance.objects.filter(mac=mac).count() > 0:
      return {'custum_state': 'FAILURE', 'msg': 'Error while creating instance: MAC address is already being used (%s)' % (mac)}

      

    # switch instance task for an instance
    new_instance = Instance.objects.create(
      name=instancetask.name,
      volume=instancetask.volume,
      user=instancetask.user,
      creator=instancetask.creator,
      vcpu=instancetask.vcpu,
      memory=instancetask.memory,
      disk=instancetask.disk,
      created=instancetask.created,
      mac=mac,
      network=network_address,
      initialised=False,
    )
    new_instance.save()
    instancetask.delete(False)
  except libvirt.libvirtError as e:
    return {'custom_state': 'FAILURE', 'msg': 'Error while creating instance: %s' % (e)}

  
    
