from django.db import models
from apps.hypervisor.models import Hypervisor
from utils import node

class InstallationDisk(models.Model):
  name = models.CharField(max_length=100)
  hypervisor = models.ForeignKey(Hypervisor)
  url = models.URLField()
  filename = models.CharField(max_length=100)

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

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "Downloading: %s [%s]" % (self.name, self.hypervisor)

  def get_status(self):
    status = node.check_command(self.hypervisor, self.task_id)
