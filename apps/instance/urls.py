from django.conf.urls.defaults import *

urlpatterns = patterns('apps.instance.views',
  url(r'^add/', 'add'),
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
  url(r'^(?P<name>[0-9a-f]+)/', 'instance'),
  url(r'^$', 'index'),
)
