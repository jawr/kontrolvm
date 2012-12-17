from django.conf.urls.defaults import *

urlpatterns = patterns('apps.installationdisk.views',
  url(r'^restart/(?P<pk>\d+)/', 'restart'),
  url(r'^delete/(?P<pk>\d+)/', 'delete'),
  url(r'^add/', 'add'),
  url(r'^$', 'index'),
)
