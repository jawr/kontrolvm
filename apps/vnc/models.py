from django.db import models
from django.contrib.auth.models import User
from apps.instance.models import Instance
import random

class Session(models.Model):
  user = models.ForeignKey(User)
  instance = models.ForeignKey(Instance)
  started = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  port = models.IntegerField()
  active = models.BooleanField(default=True)

  def __str__(self):
    return unicode(self).encode('utf-8')

  def __unicode__(self):
    return "%s (%s) %s (%s)" % (self.user, self.instance, self.started, self.active)

  """
    Get a random port, should be able to change the range somewhere
  """
  @staticmethod
  def get_random_port():
    while True:
      port = random.randrange(10000,20000)
      try:
        session = Session.objects.get(port=port, active=True)
      except Session.DoesNotExist:
        return port
