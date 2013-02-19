from django.db import models

class Size(models.Model):
  name = models.CharField(max_length=20)
  size = models.BigIntegerField(unique=True)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s (%d)" % (self.name, self.size)
