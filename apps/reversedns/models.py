from django.db import models
from django.contrib.auth.models import User
from apps.network.models import InstanceNetwork
from apps.instance.models import Instance

class ReverseDNS(models.Model):
  net = models.ForeignKey(InstanceNetwork)
  instance = models.ForeignKey(Instance)
  rdns = models.CharField(max_length=255)
  approved_by = models.ForeignKey(User)
  approved = models.DateTimeField(auto_now_add=True)
  deleted = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return unicode(self).encode('utf-8')
  
  def __unicode__(self):
    return "%s // %s" % (self.rdns, self.instance)

class ReverseDNSRequest(models.Model):
  net = models.ForeignKey(InstanceNetwork)
  instance = models.ForeignKey(Instance)
  rdns = models.CharField(max_length=255)
  requested = models.DateTimeField(auto_now_add=True)
  requestor = models.ForeignKey(User)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s // %s" % (self.rdns, self.instance)
