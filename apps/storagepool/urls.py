from django.conf.urls.defaults import *

urlpatterns = patterns('apps.storagepool.views',
  url(r'^update/(?P<pk>\d+)/', 'update'),
  url(r'^delete/(?P<pk>\d+)/', 'delete'),
  url(r'^edit/$', 'edit'),
  url(r'^add/$', 'add'),
  url(r'^$', 'index'),
)
