from django.conf.urls.defaults import *

urlpatterns = patterns('apps.instance.views',
  url(r'^base/search/', 'base_search'),
  url(r'^base/(?P<name>[0-9a-f]+)/', 'base'),
  url(r'^base/', 'base_index'),
  url(r'^clone/(?P<name>[0-9a-f]+)/', 'clone'),
  url(r'^clone/', 'clone'),
  url(r'^add/', 'add'),
  url(r'^search/', 'search'),
  url(r'^start/(?P<name>[0-9a-f]+)/', 'start'),
  url(r'^resume/(?P<name>[0-9a-f]+)/', 'resume'),
  url(r'^suspend/(?P<name>[0-9a-f]+)/', 'suspend'),
  url(r'^shutdown/(?P<name>[0-9a-f]+)/', 'shutdown'),
  url(r'^force/(?P<name>[0-9a-f]+)/', 'force'),
  url(r'^restart/(?P<name>[0-9a-f]+)/', 'restart'),
  url(r'^update/(?P<name>[0-9a-f]+)/', 'update'),
  url(r'^delete/(?P<name>[0-9a-f]+)/', 'delete'),
  url(r'^delete-task/(?P<pk>\d+)/', 'delete_task'),
  url(r'^edit/', 'edit'),
  url(r'^network/delete/(?P<pk>\d+)/', 'network_delete'),
  url(r'^network/add/(?P<name>[\da-f]+)/', 'network_add'),
  url(r'^(?P<name>[0-9a-f]+)/(?P<form>[a-z_]+)/', 'instance_form'),
  url(r'^(?P<name>[0-9a-f]+)/', 'instance'),
  url(r'^$', 'index'),
)
