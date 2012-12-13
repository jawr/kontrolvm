from django.db import models
from django.contrib.auth.models import User, check_password

class UserProfile(models.Model):
  user = models.ForeignKey(User, unique=True)
 
  def __unicode__(self):
    return "%s's Profile" % (self.user.username)
 
  def __str__(self):
    return unicode(self).encode('utf-8')

"""
  This model is used to log the various different types of browsers
  used by users.
"""
class UserBrowser(models.Model):
  name = models.CharField(max_length=200)

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
