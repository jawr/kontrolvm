from django.conf.urls.defaults import *

urlpatterns = patterns('apps.installationdisk.views',
  url(r'^add/', 'add'),
  url(r'^$', 'index'),
)
