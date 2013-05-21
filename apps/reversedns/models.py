from django.db import models
from django.contrib.auth.models import User
from apps.instance.models import Instance

class ReverseDNS(models.Model):
  instance = models.OneToOneField(Instance)
  name = models.CharField(max_length=255)
  approved_by = models.ForeignKey(User)
  aproved = models.DateTimeField(auto_now_add=True)
  deleted = models.DateTimeField(null=True, blank=True)

  def __str__(self):
    return unicode(self).encode('utf-8')
  
  def __unicode__(self):
    return "%s // %s" % (self.name, self.instance)

class ReverseDNSRequest(models.Model):
  instance = models.OneToOneField(Instance)
  name = models.CharField(max_length=255)
  requested = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return "%s // %s" % (self.name, self.instance)

  def __unicode__(self):
    return "%s // %s" % (self.name, self.instance)
