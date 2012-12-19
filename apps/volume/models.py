from django.db import models
from apps.storagepool.models import StoragePool

class Volume(models.Model):
  name = models.CharField(max_length=100)
  storagepool = models.ForeignKey(StoragePool)
  capacity = models.IntegerField(default=0)
  allocated = models.IntegerField(default=0)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return '%s on %s' % (self.name, self.hypervisor)
