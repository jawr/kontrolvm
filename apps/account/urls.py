from django.conf.urls.defaults import *
from django.views.generic.simple import direct_to_template
urlpatterns = patterns('apps.account.views',
  url(r'^login', 'account_login'),
  url(r'^logout', 'account_logout'),
  url(r'^$', 'index'),
  url(r'^admin', 'admin'),
  url(r'^add', 'add'),
  url(r'^success', direct_to_template, {'template': 'account/success.html'}),
)
