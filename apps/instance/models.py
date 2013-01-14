from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from apps.volume.models import Volume
from apps.installationdisk.models import InstallationDisk
from apps.storagepool.models import StoragePool
from binascii import hexlify
import libvirt
import persistent_messages
import os
from celery.result import AsyncResult

class Instance(models.Model):
  name = models.CharField(max_length=100)
  volume = models.OneToOneField(Volume)
  user = models.ForeignKey(User, related_name="instance_user")
  creator = models.ForeignKey(User)
  # virtual attributes
  vcpu = models.IntegerField(max_length=2, default=1)
  memory = models.IntegerField(default=268435456) # 256MB
  disk = models.ForeignKey(InstallationDisk, null=True, blank=True)
  # time fields
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)
  # status
  NOSTATE = 0
  RUNNING = 1
  BLOCKED = 2
  PAUSED = 3
  SHUTTINGDOWN = 4
  SHUTDOWN = 5
  CRASHED = 6
  SUSPENDED = 7
  LAST = 8
  NONE = 9
  STATUS_CHOICES = (
    (NOSTATE, 'No State - Hypervisor may be down'),
    (RUNNING, 'Running'),
    (BLOCKED, 'Blocked'),
    (PAUSED, 'Paused'),
    (SHUTTINGDOWN, 'Shutting Down'),
    (SHUTDOWN, 'Shutdown'),
    (CRASHED, 'Crashed'),
    (SUSPENDED, 'Suspended'),
    (LAST, 'Last'),
    (NONE, 'None'),
  )
  status = models.IntegerField(max_length=1, choices=STATUS_CHOICES, default=NONE)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s [%d CPU/%d MB RAM][%d GB][%s]" % \
      (self.user, self.vcpu, (self.memory/1024/1024.0), (self.volume.capacity/1024/1024/1024.0), self.get_status_display())

  def get_instance(self):
    hypervisor = self.volume.storagepool.hypervisor.get_connection()
    instance = None
    if hypervisor:
      try:
        instance = hypervisor.lookupByName(self.name)
      except libvirt.libvirtError:
        pass
    if not instance: 
      self.status = self.NOSTATE
      self.save()
    return instance

  def update(self, force=False):
    if not force and (timezone.now() - self.updated) < timedelta(seconds=15): return
    instance = self.get_instance()
    if instance:
      (status, na, memory, vcpu, na) = instance.info()
      self.status = status
      self.save()

  def delete(self, request=None):
    instance = self.get_instance()
    if instance:
      try:
        instance.destroy()
        instance.undefine()
        self.volume.delete(True)
        if request:
          persistent_messages.add_message(request, persistent_messages.SUCCESS, 'Deleted Instance %s' % (self))
          if request.user != self.user:
            persistent_messages.add_message(request, persistent_messages.SUCCESS, 'Deleted Instance %s' % (self), user=self.user)
        super(Instance, self).delete()
      except libvirt.libvirtError as e:
        if request:
          persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Instance %s: %s' % (self, e))
          if request.user != self.user:
            persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Instance %s' % (self), user=self.user)
  
    elif request:
      persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to get instance object inorder to delete Instance %s' % (self))
      if request.user != self.user:
        persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Instance %s' % (self), user=self.user)

      

class InstanceTask(models.Model):
  name = models.CharField(max_length=100)
  user = models.ForeignKey(User, related_name="instancetask_user")
  storagepool = models.ForeignKey(StoragePool)
  creator = models.ForeignKey(User)
  vcpu = models.IntegerField(max_length=2, default=1)
  memory = models.IntegerField(default=268435456) # 256MB
  capacity = models.BigIntegerField(default=1073741824) # 1GB
  disk = models.ForeignKey(InstallationDisk, null=True, blank=True)
  volume = models.OneToOneField(Volume, null=True, blank=True)
  # time fields
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)
  # task attributes
  task_id = models.CharField(max_length=100, default='dummy')
  percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
  message = models.CharField(max_length=255, default='N/A')
  state = models.CharField(max_length=50, default='STARTING')

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "Creating: %s [%d CPU/%d MB RAM][%d GB][%s]" % \
      (self.user, self.vcpu, (self.memory/1024/1024.0), (self.capacity/1024/1024/1024.0), self.state)

  def abort(self, request=None):
    pass

  def delete(self, purge=True):
    if self.volume and purge:
      if self.volume.delete():
        super(InstanceTask, self).delete()
    else:
      super(InstanceTask, self).delete()

  def update(self):
    task = AsyncResult(self.task_id)
    status = task.result
    if not status: return
    self.state = task.state
    if 'custom_state' in status:
      self.state = status['custom_state']
    if 'msg' in status:
      self.message = status['msg']
    if 'percent' in status:
      self.percent = int(status['percent'])
    self.save()

  """
    Used to create a random name.
  """
  @staticmethod
  def get_random_name():
    while True:
      name = hexlify(os.urandom(16))
      try:
        volume = InstanceTask.objects.get(name=name)
      except InstanceTask.DoesNotExist:
        try:
          volume = Instance.objects.get(name=name)
        except Instance.DoesNotExist:
          return name
