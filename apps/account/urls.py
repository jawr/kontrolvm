from django.conf.urls.defaults import *

urlpatterns = patterns('apps.account.views',
  url(r'^login', 'account_login'),
  url(r'^logout', 'account_logout'),
  url(r'^$', 'index'),
  url(r'^admin', 'admin'),
)
