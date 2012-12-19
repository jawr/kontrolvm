from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from xml.dom import minidom
from celery import task
from apps.hypervisor.models import Hypervisor
from apps.storagepool.models import StoragePool
from apps.installationdisk.models import InstallationDisk
from utils import node
import libvirt
import time

@task()
def initalize_hypervisor(hypervisor):
  conn = hypervisor.get_connection(True)
  if conn:
    # get a list of existing storage pools
    for pool in conn.listStoragePools():
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
    # get a list of existing installation disks
    task_id = node.send_command(hypervisor, 'installationdisk_list', 
      {'path': hypervisor.install_medium_path})
    now = time.time()
    while True:
      time.sleep(2.5)
      status = node.check_command(hypervisor, task_id)
      print status
      if status['state'] == 'SUCCESS':
        print status['args']['disks']
        for disk in status['args']['disks']:
          print disk
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
    initalize_hypervisor(instance)
