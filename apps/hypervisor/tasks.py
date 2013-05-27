from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from xml.dom import minidom
from celery import task
from apps.hypervisor.models import Hypervisor
from apps.storagepool.models import StoragePool
from apps.installationdisk.models import InstallationDisk
from apps.volume.models import Volume
from apps.instance.models import Instance
from apps.network.models import Network, InstanceNetwork
from apps.shared.models import Size
from utils import node
import libvirt
import time
import re

match_vol = re.compile('\.qcow2$')

def initalize_hypervisor_instances(hypervisor):
  conn = hypervisor.get_connection(True)
  if conn:
    # create dummy network
    network, created = Network.objects.get_or_create(
      hypervisor=hypervisor,
      netmask="255.255.255.255",
      gateway="0.0.0.0",
      broadcast="0.0.0.255",
      network="0.0.0.0",
      start="0.0.0.0",
      end="255.255.255.255"
    )

    domains = []
    for dom_id in conn.listDomainsID():
      dom = conn.lookupByID(dom_id)
      xml = minidom.parseString(dom.XMLDesc(0))
      items = xml.getElementsByTagName('name')
      name = items[0].childNodes[0].data
      domains.append(name)
    domains += conn.listDefinedDomains()
    print domains
    dummy_user = User.objects.all()[0]
    for name in domains:
      print name
      dom = conn.lookupByName(name)
      xml = minidom.parseString(dom.XMLDesc(0))
      items = xml.getElementsByTagName('memory')
      memory = int(items[0].childNodes[0].data)
      memory_size = Size.objects.filter(size=memory*1024)
      if not memory_size:
        memory_size, created = Size.objects.get_or_create(
          name="%d KiB" % (memory), # make more robust, i.e. detect unit size
          size=memory*1024
        )
      else: memory_size = memory_size[0]
      items = xml.getElementsByTagName('vcpu')
      vcpus = int(items[0].childNodes[0].data)
      items = xml.getElementsByTagName('mac')
      mac = items[0].getAttributeNode('address').nodeValue
      volume_path = None
      for disk in xml.getElementsByTagName('disk'):
        if disk.getAttributeNode('device').nodeValue == 'disk':
          items = disk.getElementsByTagName('source')
          volume_path = items[0].getAttributeNode('file').nodeValue
      if not volume_path:
        # print error
        print "no volume path for %s" % (name)
        continue
      try:
        vol = conn.storageVolLookupByPath(volume_path)
        storagepool = StoragePool.objects.get(
          name=vol.storagePoolLookupByVolume().name()
        )
      except libvirt.libvirtError as e:
        print e
        print "HERRRO"
        continue
      if not storagepool:
        # print error
        print "no storage pool for %s" % (name)
        continue
      capacity = Size.objects.get(size=vol.info()[1])
      if not capacity:
        capacity, created = Size.objects.get_or_create(
          name=vol.info()[1],
          size=vol.info()[1]
        )
      volume = Volume.objects.filter(name=volume_path.split('/')[-1].split('.')[0])
      if not volume:
        volume = Volume(
          name=volume_path.split('/')[-1].split('.')[0],
          capacity=capacity,
          allocated=vol.info()[2],
          storagepool=storagepool
        )
        volume.save()
      else: volume = volume[0]

      instance_network = None
      # might need to detect multiple networks here, apeend to list
#      for param in xml.getElementsByTagName('parameter'):
#        if param.getAttributeNode('name').nodeValue == 'IP':
#          instance_network = param.getAttributeNode('value').nodeValue
#      if instance_network:
#        instance_network, created = InstanceNetwork.objects.get_or_create(
#          ip=instance_network,
#          network=network,
#          
#        )
#      else:
#        instance_network = network.create_unique_address()

      print "Create instance object..."

      instance = Instance.objects.filter(name=name)
      if not instance:
        instance = Instance(
          name=name,
          user=dummy_user,
          creator=dummy_user,
          vcpu=vcpus,
          memory=memory_size,
          volume=volume,
        )
        instance.save() 
  print "DONE..." 
      

@task()
def initalize_hypervisor(hypervisor):
  conn = hypervisor.get_connection(True)
  if conn:
    # get a list of existing storage pools
    for pool in conn.listDefinedStoragePools() + conn.listStoragePools():
      storagepool = conn.storagePoolLookupByName(pool)
      xml = minidom.parseString(storagepool.XMLDesc(0))
      items = xml.getElementsByTagName('name')
      name = items[0].childNodes[0].data
      items = xml.getElementsByTagName('path')
      path = items[0].childNodes[0].data
      (new_pool, created) = StoragePool.objects.get_or_create(
        name=name,
        path=path,
        hypervisor=hypervisor
      )
      if created: new_pool.save()
      new_pool.update(True) 

    try:
      initalize_hypervisor_instances(hypervisor)
    except Exception as e:
      print "Initalize hypervisor instances error: %s" % (e)

    print "HELLO"
        
    # get a list of existing installation disks
    task_id = node.send_command(hypervisor, 'installationdisk_list', 
      {'path': hypervisor.install_medium_path})
    print task_id
    now = time.time()
    while True:
      time.sleep(2.5)
      status = node.check_command(hypervisor, task_id)
      if status['state'] == 'SUCCESS':
        for disk in status['args']['disks']:
          (installationdisk, created) = InstallationDisk.objects.get_or_create(
            name=disk['filename'],
            hypervisor=hypervisor,
            url='Unknown',
            filename=disk['filename'],
            total_bytes=disk['total_bytes'],
            user=User.objects.all()[0] # not brilliant..
          )
          if created: installationdisk.save()
        break
      elif status['state'] == 'FAILED' or status['state'] == 'ERROR' or time.time() - now > 60:
        break 

@receiver(post_save, sender=Hypervisor)
def initalize_hypervisor_signal(sender, **kwargs):
  instance = kwargs['instance']
  if instance.status == 'IN':
    initalize_hypervisor.delay(instance)

@receiver(pre_delete, sender=Hypervisor)
def cleanup_hypervisor_signal(sender, **kwargs):
  instance = kwargs['instance']
  # need to delete all associated data
