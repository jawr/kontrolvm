from django.db import models
from django.contrib import messages
from django.utils import timezone
from apps.storagepool.models import StoragePool
from apps.shared.models import Size
from datetime import timedelta
from binascii import hexlify
import persistent_messages
import os
import libvirt

class Volume(models.Model):
  name = models.CharField(max_length=100, unique=True)
  device_name = models.CharField(max_length=20, null=True, blank=True)
  storagepool = models.ForeignKey(StoragePool)
  capacity = models.ForeignKey(Size)
  allocated = models.BigIntegerField(default=0)
  # updated
  updated = models.DateTimeField(auto_now=True)

  def path(self):
    return "%s.qcow2" % (os.path.join(self.storagepool.path, self.name))

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return '%s on %s' % (self.name, self.storagepool)
  
  def get_volume(self):
    pool = self.storagepool.get_storagepool()
    if pool:
      try:
        vol = pool.storageVolLookupByName('%s.qcow2' % (self.name))
        return vol
      except libvirt.libvirtError as e:
        pass
      
    return None

  def delete(self, request=None):
    vol = self.get_volume()
    if vol:
      try:
        vol.delete(0)
        if request:
          persistent_messages.add_message(request, persistent_messages.SUCCESS, 'Deleted %s Volume' % (self))
        super(Volume, self).delete()
        return True
      except libvirt.libvirtError as e:
        if request:
          persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete %s Volume: %s' % (self, e))

    elif request:
      persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Volume: Unable to get Volume %s' % (self))
    return False 

  def update(self):
    if (timezone.now() - self.updated) < timedelta(minutes=1): return
    volume = self.get_volume()
    if volume:
      (vol_type, capacity, allocated) = volume.info()
      self.allocated = allocated
      self.save()

  def create(self, request=None):
    pool = self.storagepool.get_storagepool()
    if pool:
      xml = """
        <volume>
          <name>%s.qcow2</name>
          <capacity>%s</capacity>
          <allocation>0</allocation>
          <target>
            <format type="qcow2" />
          </target>
        </volume>""" \
          % (self.name, self.capacity.size)
      try:
        pool.createXML(xml, 0)
        return True
      except libvirt.libvirtError as e:
        if request:
          persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to create Volume %s: %s' % (self.name, e))
        return False

    else:
      persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to create Volume %s (Unable to connect to Storage Pool)' % (self.name))
      return False

  """
    Used to create a random name.
  """
  @staticmethod
  def create_random_name():
    while True:
      name = hexlify(os.urandom(16))
      try:
        volume = Volume.objects.get(name=name)
      except Volume.DoesNotExist:
        return name
