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
    (NOSTATE, 'No State'),
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
    hypervisor = self.storagepool.hypervisor.get_connection()
    if hypervisor:
      return hyper.lookupByName(self.name)
    return None 

  def update(self):
    if (timezone.now() - self.updated) < timedelta(minutes=1): return
    pass

  def delete(self, request=None):
    super(Instance, self).delete()

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

  def delete(self, request=None):
    if self.volume:
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
