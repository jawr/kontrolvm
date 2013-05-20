from django.conf.urls.defaults import *

urlpatterns = patterns('apps.snapshot.views',
  url(r'^create/(?P<name>[0-9a-f]+)/', 'create'),
  url(r'^delete/(?P<name>[0-9a-f]+)/(?P<pk>[0-9]+)/', 'delete'),
  url(r'^edit/', 'edit'),
)
