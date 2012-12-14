from django.db import models
import signal
import libvirt

"""
  Model used to wrap around a libvirt hypervisor. Offers functionality
  to return a libvirt connection object.
"""
class Hypervisor(models.Model):
  name = models.CharField(max_length=100)
  location = models.CharField(max_length=100)
  address = models.CharField(max_length=255)
  timeout = models.IntegerField(max_length=2, default=10)
  # status choices
  ONLINE = 'UP'
  TIMEOUT = 'TO'
  OFFLINE = 'DN'
  STATUS_CHOICES = (
    (ONLINE, 'Online'),
    (TIMEOUT, 'Timeout'),
    (OFFLINE, 'Offline'),
  )
  status = models.CharField(max_length=2, choices=STATUS_CHOICES, 
    default=ONLINE)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s (%s)" % (self.name, self.location)

  def get_connection(self, update=False):
    conn = None
    if self.status != 'UP' and update or self.status == 'UP':
      conn = libvirt.open(self.address)
      if not conn:
        if self.status == 'UP':
          self.status = 'TO'
    return conn 
