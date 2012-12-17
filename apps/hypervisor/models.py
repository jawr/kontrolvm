from django.db import models
import libvirt

"""
  Model used to wrap around a libvirt hypervisor. Offers functionality
  to return a libvirt connection object.
"""
class Hypervisor(models.Model):
  name = models.CharField(max_length=100)
  location = models.CharField(max_length=100)
  address = models.CharField(max_length=255)
  node_address = models.CharField(max_length=255)
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

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s [%s][%s]" % (self.name, self.location, self.get_status_display())

  def get_connection(self, update=False):
    conn = None
    if self.status != 'UP' and update or self.status == 'UP':
      try:
        conn = libvirt.open(self.address)
        if not conn:
          if self.status == 'UP': self.status = 'TO'
        else: self.status = 'UP'
        self.save()
      except libvirt.libvirtError as e:
        self.status = 'DN'
        self.save()
    return conn 
