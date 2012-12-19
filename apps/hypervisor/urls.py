from django.conf.urls.defaults import *

urlpatterns = patterns('apps.hypervisor.views',
  url(r'^add/', 'add'),
  url(r'^edit/', 'edit'),
  url(r'^start/(?P<pk>\d+)/', 'start'),
  url(r'^stop/(?P<pk>\d+)/', 'stop'),
  url(r'^update/(?P<pk>\d+)/', 'update'),
  url(r'^delete/(?P<pk>\d+)/', 'delete'),
  url(r'^$', 'index'),
)
