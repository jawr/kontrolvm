from django.db import models
from django.contrib.auth.models import User
from django.contrib import messages
from apps.instance.models import Instance
import libvirt
import persistent_messages

# snapshot xml taken from https://github.com/retspen/webvirtmgr/blob/master/virtmgr/views.py#L1411
SNAPSHOT_TEMPLATE = \
  """
    <domainsnapshot>
      <name>%s</name>
      <state>shutoff</state>
      <creationTime>%d</creationTime>
    </domainsnapshot>
  """

class Snapshot(models.Model):
  instance = models.ForeignKey(Instance)
  created = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s (%s)" % (self.instance, self.created)
