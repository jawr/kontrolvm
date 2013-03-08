from django.db import models
from django.contrib.auth.models import User, check_password
from django.db.models.signals import post_save
from apps.instance.models import Instance
from apps.vnc.models import Session

class UserAudit(models.Model):
  user = models.ForeignKey(User)
  time = models.DateTimeField(auto_now=True)
  page = models.CharField(max_length=200)
  
  def current_ip(self):
    login = UserLogin.objects.filter(user=self.user).order_by('-id')
    if not login: return "<error>"
    return login[0].address

  def current_browser(self):
    login = UserLogin.objects.filter(user=self.user).order_by('-id')
    if not login: return "<error>"
    return login[0].browser

class UserProfile(models.Model):
  user = models.ForeignKey(User, unique=True)
 
  def __unicode__(self):
    return "%s's Profile" % (self.user.username)
 
  def __str__(self):
    return unicode(self).encode('utf-8')

  def audit(self):
    return UserAudit.objects.get(user=self.user)

  def instance_count(self):
    return Instance.objects.filter(user=self.user).count()

  def vnc_session_count(self):
    return Session.objects.filter(user=self.user).count()

def create_profile(sender, **kw):
  user = kw["instance"]
  if kw["created"]:
    up = UserProfile(user=user)
    up.save()

post_save.connect(create_profile, sender=User)


class UserBrowser(models.Model):
  name = models.CharField(max_length=255, unique=True)

  def __unicode__(self):
    return self.name

  def __str__(self):
    return unicode(self).encode('utf-8')

"""
  This model is used to log a successful user login. This is useful for 
  security and support reasons.
"""
class UserLogin(models.Model):
  user = models.ForeignKey(User)
  time = models.DateTimeField(auto_now_add=True)
  address = models.GenericIPAddressField()
  browser = models.ForeignKey(UserBrowser)

  def __unicode__(self):
    return "Login: %s @ %s [%s][%s]" % (self.user, self.time, self.address, \
      self.browser)

  def __str__(self):
    return unicode(self).encode('utf-8')

"""
  This model is used to log failed logins, for the same reasons stated above.
"""
class InvalidLogin(models.Model):
  user = models.CharField(max_length=200)
  time = models.DateTimeField(auto_now_add=True)
  browser = models.ForeignKey(UserBrowser)
  address = models.GenericIPAddressField()

  def __unicode__(self):
    return "Invalid Login: %s @ %s [%s][%s]" % (self.user, self.time, self.address, \
      self.browser)

  def __str__(self):
    return unicode(self).encode('utf-8')
