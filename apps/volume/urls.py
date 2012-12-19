from django.conf.urls.defaults import *

urlpatterns = patterns('apps.volume.views',
  url(r'^delete/(?P<pk>\d+)/', 'delete'),
  url(r'^add', 'add'),
  url(r'^$', 'index'),
)
