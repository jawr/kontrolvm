from django.db import models
from apps.instance.models import Instance
import libvirt
import time

# snapshot xml taken from https://github.com/retspen/webvirtmgr/blob/master/virtmgr/views.py#L1411
SNAPSHOT_TEMPLATE = \
  """
    <domainsnapshot>
      <name>%s</name>
    </domainsnapshot>
  """

class Snapshot(models.Model):
  name = models.CharField(max_length=100, default="Snapshot")
  creating = models.BooleanField(default=True)
  status = models.CharField(max_length=200, blank=True, null=True)
  instance = models.ForeignKey(Instance)
  created = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s %s (%s - %s)" % (self.name, self.instance, self.creating, self.created)

  def get_unixtime(self):
    return int(time.mktime(self.created.timetuple())*1000)

  def get_snapshot(self):
    instance = self.instance.get_instance()
    snapshot = None
    if instance:
      try:
        snapshot = instance.snapshotLookupByName("%s_%d" % (self.instance.name, self.get_unixtime()), 0)
      except libvirt.libvirtError:
        pass
    return snapshot
