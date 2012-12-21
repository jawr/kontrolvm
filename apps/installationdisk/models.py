from django.db import models
from django.contrib.auth.models import User
from django.contrib import messages
from apps.hypervisor.models import Hypervisor
from utils import node
import persistent_messages
import time
import os

class InstallationDisk(models.Model):
  name = models.CharField(max_length=100)
  hypervisor = models.ForeignKey(Hypervisor)
  url = models.URLField()
  filename = models.CharField(max_length=100)
  total_bytes = models.IntegerField()
  user = models.ForeignKey(User)

  def path(self):
    return "%s" % (os.path.join(self.hypervisor.install_medium_path, self.filename))

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s [%s]" % (self.name, self.hypervisor)

  """
    Cleanup disk on node.
  """
  def delete(self, request=None):
    task_id = node.send_command(self.hypervisor, 'installationdisk_delete', {
      'path': os.path.join(self.hypervisor.install_medium_path, self.filename)})
    now = time.time()
    while True:
      time.sleep(2.5)
      status = node.check_command(self.hypervisor, task_id)
      print status
      if status['state'] == 'SUCCESS':
        if request:
          messages.add_message(request, persistent_messages.SUCCESS, 'Deleted Installation Disk %s on %s' % (self.name, self.hypervisor))
        super(InstallationDisk, self).delete()
        break
      elif status['state'] == 'FAILED' or status['state'] == 'ERROR':
        if request:
          msg = "N/A"
          if 'args' in status:
            msg = status['args']['msg']
          messages.add_message(request, persistent_messages.ERROR, 'Unable to delete Installation Disk %s on %s: %s' % (self.name, self.hypervisor, msg))
        break

class InstallationDiskTask(models.Model):
  name = models.CharField(max_length=100)
  hypervisor = models.ForeignKey(Hypervisor)
  url = models.URLField()
  filename = models.CharField(max_length=100)
  task_id = models.CharField(max_length=100, default='dummy')
  total_bytes_dl = models.IntegerField(default=0)
  total_bytes = models.IntegerField(default=0)
  percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
  state = models.CharField(max_length=50)
  user = models.ForeignKey(User)
  

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "Downloading: %s [%s]" % (self.name, self.hypervisor)

  def start(self):
    self.total_bytes_dl = 0
    self.total_bytes = 0
    self.percent = 0
    self.task_id = node.send_command(self.hypervisor, 'installationdisk_download', 
    {
      'url': self.url, 
      'path': self.hypervisor.install_medium_path
    })
    self.save()

  def abort(self):
    ret = node.abort_command(self.hypervisor, self.task_id)
    if 'state' in ret:
      self.state = ret['state']
      self.save()

  def get_status(self):
    status = node.check_command(self.hypervisor, self.task_id)
    print status
    if 'args' in status:
      args = status['args']
      if args:
        if 'total_bytes_dl' in args:
          self.total_bytes_dl = args['total_bytes_dl']
        if 'total_bytes' in args:
          self.total_bytes = args['total_bytes']
        if 'percent' in args:
          self.percent = args['percent']

    self.state = status['state']
    self.save()
