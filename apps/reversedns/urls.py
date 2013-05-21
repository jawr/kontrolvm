from django.conf.urls.defaults import *

urlpatterns = patterns('apps.reversedns.views',
  url(r'^request/', 'request'),
  url(r'^approve/(?P<pk>[0-9]+)/', 'approve'),
  url(r'^$', 'index'),
)
