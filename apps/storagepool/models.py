from django.db import models
from apps.hypervisor.models import Hypervisor
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import libvirt
import persistent_messages

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
  # more details
  capacity = models.BigIntegerField(default=0)
  allocated = models.BigIntegerField(default=0)
  percent = models.IntegerField(default=0)
  available = models.BigIntegerField(default=0)
  percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
  # updated
  updated = models.DateTimeField(auto_now=True)
  
  class Meta:
    unique_together = ('name', 'hypervisor')

  def __str__(self):
    return unicode(self).encode('utf-8')
  
  def __unicode__(self):
    return "%s [%s][%s]" % (self.name, self.hypervisor, self.get_status_display())

  def get_storagepool(self):
    storagepool = None
    try:
      if self.hypervisor.status == 'UP':
        conn = self.hypervisor.get_connection()
        if conn: 
          storagepool = conn.storagePoolLookupByName(self.name)
          if not storagepool.isActive(): storagepool = None
          
    except libvirt.libvirtError:
      pass
    return storagepool

  def delete(self, request=None):
    storagepool = self.get_storagepool()
    if storagepool:
      if storagepool.info()[0] == 2:
        # delete any associated volumes
        for vol in storagepool.listVolumes():
          try:
            vol = storagepool.storageVolLookupByName(vol)
            vol.delete(0)
          except libvirt.libvirtError as e:
            if request:
              messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Storage Pool Volume: %s' % (e))
            # try and continue
        # set pool to inactive
        try:
          storagepool.destroy()
        except libvirt.libvirtError as e:
          if request:
            messages.add_message(request, persistent_messages.ERROR, 
              'Unable to destroy Storage Pool: %s' % (e))
            return
      # delete and undefine the pool
      try:
        storagepool.delete(0)
        storagepool.undefine()
      except libvirt.libvirtError as e:
        if request:
          messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Storage Pool: %s' % (e))
        return
      if request:
        messages.add_message(request, persistent_messages.SUCCESS,
          'Deleted Storage Pool: %s [%s][%s]' % (self.name, self.path, self.hypervisor))
      # delete the model
      super(StoragePool, self).delete()
    elif request:
      messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Storage Pool: Unable to get Storage Pool %s' % (self))
    

  def update(self):
    # check if we have checked in the last minute
    if (timezone.now() - self.updated) < timedelta(minutes=1): return
    storagepool = self.get_storagepool()
    if storagepool:
      
      (status, capacity, allocated, available) = storagepool.info()
      self.status = status
      self.capacity = capacity
      self.allocated = allocated
      self.available = available
      self.percent = ((float(allocated)/float(capacity))*100)
      self.save()
