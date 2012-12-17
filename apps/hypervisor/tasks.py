from django.db.models.signals import post_save
from django.dispatch import receiver
from xml.dom import minidom
from celery import task
from apps.storagepool.models import Hypervisor
from apps.storagepool.models import StoragePool
import libvirt

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

@receiver(post_save, sender=Hypervisor)
def initalize_hypervisor_signal(sender, **kwargs):
  instance = kwargs['instance']
  if instance.status == 'IN':
    initalize_hypervisor(instance)
