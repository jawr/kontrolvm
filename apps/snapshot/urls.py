from django.conf.urls.defaults import *

urlpatterns = patterns('apps.snapshot.views',
  url(r'^create/(?P<name>[0-9a-f]+)/', 'create'),
)