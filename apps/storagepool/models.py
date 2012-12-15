from django.db import models
from apps.hypervisor.models import Hypervisor

"""
  Model used to wrap around a hypervisors storage pool.
"""
class StoragePool(models.Model):
  name = models.CharField(max_length=100)
  hypervisor = models.ForeignKey(Hypervisor)
  path = models.CharField(max_length=255)
  # status choices
  INACTIVE = 0
  BUILDING = 1
  RUNNING = 2
  DEGRADED = 3
  INACCESSIBLE = 4
  LAST = 5
  NONE = 6
  STATUS_CHOICES = (
    (INACTIVE, 'Inactive'),
    (BUILDING, 'Buidling'),
    (RUNNING, 'Running'),
    (DEGRADED, 'Degraded'),
    (INACCESSIBLE, 'Inaccessible'),
    (LAST, 'Last'),
    (NONE, 'None'),
  )
  status = models.IntegerField(max_length=1, choices=STATUS_CHOICES, default=NONE)
  
  def __str__(self):
    return unicode(self).encode('utf-8')
  
  def __unicode__(self):
    return "%s [%s][%s]" % (self.name, self.hypervisor, self.get_status_display())

  def get_storagepool(self):
    storagepool = None
    if self.hypervisor.status == 'UP':
      conn = self.hypervisor.get_connection()
      storagepool = conn.storagePoolLookupByName(self.name)
    return storagepool
