from django.conf.urls.defaults import *

urlpatterns = patterns('apps.volume.views',
  url(r'^add', 'add'),
  url(r'^$', 'index'),
)
