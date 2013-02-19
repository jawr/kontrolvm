from django.db import models
from apps.shared.models import Size
from utils.node import send_command
import libvirt

class Instance(object): pass
class StoragePool(object): pass

"""
  Model used to wrap around a libvirt hypervisor. Offers functionality
  to return a libvirt connection object.
"""
class Hypervisor(models.Model):
  name = models.CharField(max_length=100)
  location = models.CharField(max_length=100)
  address = models.CharField(max_length=255)
  libvirt_port = models.IntegerField(default=16509)
  node_port = models.IntegerField(default=5000)
  timeout = models.IntegerField(max_length=2, default=10)
  # status choices
  ONLINE = 'UP'
  TIMEOUT = 'TO'
  OFFLINE = 'DN'
  INIT = 'IN'
  STATUS_CHOICES = (
    (ONLINE, 'Online'),
    (TIMEOUT, 'Timeout'),
    (OFFLINE, 'Offline'),
    (INIT, 'Initalize'),
  )
  status = models.CharField(max_length=2, choices=STATUS_CHOICES, 
    default=INIT)
  # install medium path
  install_medium_path = models.CharField(max_length=255)
  # limits
  maximum_memory = models.ForeignKey(Size, related_name="hypervisor_max_memory")
  maximum_vcpus = models.IntegerField()
  maximum_hdd = models.ForeignKey(Size, related_name="hypervisor_max_hdd")

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return '%s [%s][%s]' % (self.name, self.location, self.get_status_display())

  def get_libvirt_address(self):
    return "qemu+tcp://%s:%d/system" % (self.address, self.libvirt_port)

  def get_node_address(self):
    return "http://%s:%d" % (self.address, self.node_port)

  def get_libvirt_status_html(self):
    conn = self.get_connection()
    if conn:
      return '<span class="label label-success">Responding</span>'
    return '<span class="label label-error">Not Responding</span>'

  def get_node_status_html(self):
    if send_command(self, 'check', {}):
      return '<span class="label label-success">Responding</span>'
    return '<span class="label label-error">Not Responding</span>'

  def get_connection(self, update=False):
    conn = None
    if self.status != 'UP' and update or self.status == 'UP':
      try:
        conn = libvirt.open(self.get_libvirt_address())
        if not conn:
          if self.status == 'UP': self.status = 'TO'
        else: self.status = 'UP'
        self.save()
      except libvirt.libvirtError as e:
        self.status = 'DN'
        self.save()
    return conn 

  def start(self):
    self.status = self.ONLINE
    self.save()

  def stop(self):
    self.status = self.OFFLINE
    self.save()
