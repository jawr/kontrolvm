from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta
from apps.volume.models import Volume
from apps.shared.models import Size
from apps.installationdisk.models import InstallationDisk
from apps.storagepool.models import StoragePool
from binascii import hexlify
from xml.etree import ElementTree
import libvirt
import persistent_messages
import os
import string
import time
import simplejson
from utils import node
from random import choice
from celery.result import AsyncResult

# template taken from: http://virtips.virtwind.com/2012/05/attaching-disk-via-libvirt-using-python/
ATTACH_DISK_TEMPLATE = \
  """
    <disk type='file' device='cdrom'>
        <driver name='qemu' type='raw'/>
        <source file='{path}'/>
        <target dev='hdc' bus='ide'/>
        <readonly/>
    </disk>
  """
DETACH_DISK_TEMPLATE = \
  """
    <disk type='file' device='cdrom'>
        <driver name='qemu' type='raw'/>
        <target dev='hdc' bus='ide'/>
    </disk>
  """


ATTACH_NETWORK_TEMPLATE = \
  """
    <interface type='bridge'>
        <source bridge='{device}' />
        <filterref filter='clean-traffic'>
          <parameter name='IP' value='{ip}' />
        </filterref>
        <model type='virtio'/>
        <alias name='{alias}'/>
    </interface>
  """
DETACH_NETWORK_TEMPLATE = \
  """
    <interface type='bridge'>
        <source bridge='{device}' />
        <alias name='{alias}'/>
        <mac address='{mac}'/>
    </interface>
  """

class Instance(models.Model):
  name = models.CharField(max_length=100)
  alias = models.CharField(max_length=100, default="My Instance", null=True, blank=True)
  volume = models.OneToOneField(Volume)
  user = models.ForeignKey(User, related_name="instance_user")
  creator = models.ForeignKey(User)
  # virtual attributes
  vcpu = models.IntegerField(max_length=2, default=1)
  memory = models.ForeignKey(Size, related_name="instance_memory")
  disk = models.ForeignKey(InstallationDisk, null=True, blank=True)
  # time fields
  updated = models.DateTimeField(auto_now=True)
  created = models.DateTimeField(auto_now_add=True)
  initialised = models.BooleanField(default=False)
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
  base = models.BooleanField(default=False, editable=False)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s / %d VCPUs / %s RAM / %s HDD / %s" % (self.alias, self.vcpu, self.memory.name, self.volume.capacity.name, self.name)

  def get_xml(self):
    dom = self.get_instance()
    if dom: 
      try:
        return dom.XMLDesc(0)
      except libvirt.libvirtError as e:
        return e
    return  "Error"

  def get_vnc_port(self):
    instance = self.get_instance()
    if not instance: return 0
    tree = ElementTree.fromstring(instance.XMLDesc(0))
    graphics = tree.findall('devices/graphics')
    return int(graphics[0].get('port'))

  def get_status_html(self):
    if self.status == 1:
      return '<span class="label label-success">%s</span>' % (self.get_status_display())
    return '<span class="label label-warning">%s</span>' % (self.get_status_display())

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
        try:
          # shutdown/destroy the vm if it's still up and running. 
          instance.destroy()
        except libvirt.libvirtError as e:
          if str(e) != 'Requested operation is not valid: domain is not running': raise e
        instance.undefine()
        self.volume.delete(request)
        if request:
          persistent_messages.add_message(request, persistent_messages.SUCCESS, 'Deleted Instance %s' % (self))
          if request.user != self.user:
            persistent_messages.add_message(request, persistent_messages.SUCCESS, 'Deleted Instance %s' % (self), user=self.user)
        super(Instance, self).delete()
      except libvirt.libvirtError as e:
        print e
        print type(e)
        if request:
          persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Instance %s: %s' % (self, e))
          if request.user != self.user:
            persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Instance %s' % (self), user=self.user)
  
    elif request:
      persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to get instance object inorder to delete Instance %s' % (self))
      if request.user != self.user:
        persistent_messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Instance %s' % (self), user=self.user)

  def detach_disk(self, request=None):
    dom = self.get_instance()
    if dom:
      try:
        dom.updateDeviceFlags(DETACH_DISK_TEMPLATE, 0)
        self.disk = None
        self.save()
        if request:
          messages.add_message(request, persistent_messages.SUCCESS, 'Unmounted disk on %s' % (self.name))
      except libvirt.libvirtError as e:
        if request and request.user.is_staff:
          messages.add_message(request, persistent_messages.ERROR, 'Unable to unmount disk on %s, unable to get dom: %s' % (self.name, e))
        elif request:
          messages.add_message(request, persistent_messages.ERROR, 'Unable to unmount diskon %s' % (self.name))

    elif request and request.user.is_staff:
      messages.add_message(request, persistent_messages.ERROR, 'Unable to unmount disk on %s, unable to get dom' % (self.name))
    elif request:
      messages.add_message(request, persistent_messages.ERROR, 'Unable to unmount disk on %s' % (self.name))

  def attach_network(self, address, request=None, first=False):
    dom = self.get_instance()
    if dom:
      template = ATTACH_NETWORK_TEMPLATE.format(
        ip=address.ip,
        device=address.network.device,
        alias=address.ip
      )
      try:
        dom.attachDeviceFlags(template, 0)
        tree = ElementTree.fromstring(dom.XMLDesc(0))
        for i in tree.findall('devices/interface'):
          for p in i.findall('filterref/parameter'):
            if p.get('value') == address.ip:
              mac = i.find('mac').get('address').upper()
              address.mac = mac
              address.save()
        resp = node.send_command(address.network.hypervisor, "network_track_ip", {'ip': address.ip})
        if resp:
          print resp
      except libvirt.libvirtError as e:
        print e

  def detach_network(self, address, request=None):
    dom = self.get_instance()
    if dom:
      template = DETACH_NETWORK_TEMPLATE.format(alias=address.ip, device=address.network.device, mac=address.mac)
      try:
        dom.detachDeviceFlags(template, 0)
        address.delete()
        resp = node.send_command(address.network.hypervisor, "network_remove_ip", {'ip': address.ip})
        if resp:
          print resp
      except libvirt.libvirtError as e:
        print e 

  def attach_disk(self, disk, request=None):
    if disk == None:
      self.detach_disk(request)
      return
    dom = self.get_instance()
    if dom:
      template = ATTACH_DISK_TEMPLATE.format(path=disk.path())
      print template
      try:
        dom.updateDeviceFlags(template, 0)
        self.disk = disk
        self.save()
        messages.add_message(request, persistent_messages.SUCCESS, 'Mounted Disk %s on %s' % (disk, self.name))
      except libvirt.libvirtError as e:
        if request and request.user.is_staff:
          messages.add_message(request, persistent_messages.ERROR, 'Unable to mount %s on %s, unable to get dom: %s' % (disk, self.name, e))
        elif request:
          messages.add_message(request, persistent_messages.ERROR, 'Unable to mount %s on %s' % (disk, self.name))

    elif request and request.user.is_staff:
      messages.add_message(request, persistent_messages.ERROR, 'Unable to mount %s on %s, unable to get dom' % (disk, self.name))
    elif request:
      messages.add_message(request, persistent_messages.ERROR, 'Unable to mount %s on %s' % (disk, self.name))

  def create_random_vnc_password(self, request=None):
    instance = self.get_instance()
    if instance == None:
      if request:
        messages.add_message(request, persistent_messages.ERRPR, 'Unable to get instance in order to create a random VNC password')
      return

    xml = ElementTree.fromstring(instance.XMLDesc(0))
    graphic_element = xml.find('.//graphics')
    passwd = ''.join(choice(string.letters + string.digits) for _ in xrange(8)) 
    graphic_element.attrib['passwd'] = passwd
    try:
      instance.updateDeviceFlags(ElementTree.tostring(graphic_element), 0)
    except libvirt.libvirtError as e:
      if request and request.user.is_staff:
        messages.add_message(request, persistent_messages.ERROR, 'Unable to create random VNC password on %s, error: %s' % (self.name, e))
      elif request:
        messages.add_message(request, persistent_messages.ERROR, 'Unable to create random VNC password on %s' % (self.name))
      return ""
    return passwd
    
  def get_vnc_password(self, request=None):
    return self.create_random_vnc_password(request)

class InstanceCloneTask(models.Model):
  name = models.CharField(max_length=100)
  base = models.ForeignKey(Instance)
  user = models.ForeignKey(User, related_name="instanceclonetask_user")
  creator = models.ForeignKey(User)
  vcpu = models.IntegerField(max_length=2, default=1)
  memory = models.ForeignKey(Size, related_name="instanceclonetask_memory")
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
    return "Cloning: %s [%d CPU/%s RAM/%s HDD][%s]" % \
      (self.base.alias, self.vcpu, (self.memory.name), (self.capacity.name), self.state)

class InstanceTask(models.Model):
  name = models.CharField(max_length=100)
  user = models.ForeignKey(User, related_name="instancetask_user")
  storagepool = models.ForeignKey(StoragePool)
  creator = models.ForeignKey(User)
  vcpu = models.IntegerField(max_length=2, default=1)
  memory = models.ForeignKey(Size, related_name="instancetask_memory")
  capacity = models.ForeignKey(Size, related_name="instancetask_capacity")
  disk = models.ForeignKey(InstallationDisk, null=True, blank=True)
  volume = models.OneToOneField(Volume, null=True, blank=True)
  network = models.ForeignKey('network.Network')
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
    return "Creating: %s [%d CPU/%s RAM/%s HDD][%s]" % \
      (self.user, self.vcpu, (self.memory.name), (self.capacity.name), self.state)

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
