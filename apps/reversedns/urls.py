from django.conf.urls.defaults import *

urlpatterns = patterns('apps.reversedns.views',
  url(r'^request/(?P<id>[0-9]+)/(?P<name>[0-9a-f]+)/', 'request'),
  url(r'^approved/', 'approved'),
  url(r'^approve/(?P<id>[0-9]+)/', 'approve'),
  url(r'^$', 'requests'),
)
