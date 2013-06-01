from django.conf.urls.defaults import *

urlpatterns = patterns('apps.network.views',
  url(r'^add/', 'add'),
  url(r'^edit/', 'edit'),
  url(r'^delete/(?P<pk>\d+)/', 'delete'),
  url(r'$', 'index'),
)
