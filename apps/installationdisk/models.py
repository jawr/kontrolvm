from django.db import models
from apps.hypervisor.models import Hypervisor
from utils import node

class InstallationDisk(models.Model):
  name = models.CharField(max_length=100)
  hypervisor = models.ForeignKey(Hypervisor)
  url = models.URLField()
  filename = models.CharField(max_length=100)
  total_bytes = models.IntegerField()

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s [%s]" % (self.name, self.hypervisor)

class InstallationDiskTask(models.Model):
  name = models.CharField(max_length=100)
  hypervisor = models.ForeignKey(Hypervisor)
  url = models.URLField()
  filename = models.CharField(max_length=100)
  task_id = models.CharField(max_length=100)
  total_bytes_dl = models.IntegerField(default=0)
  total_bytes = models.IntegerField(default=0)
  percent = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
  

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "Downloading: %s [%s]" % (self.name, self.hypervisor)

  def get_status(self):
    status = node.check_command(self.hypervisor, self.task_id)
    if 'args' in status:
      args = status['args']
      if 'total_bytes_dl' in args:
        self.total_bytes_dl = args['total_bytes_dl']
      if 'total_bytes' in args:
        self.total_bytes = args['total_bytes']
      if 'percent' in args:
        self.percent = args['percent']
      self.save()

    return status['state']
