from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseRedirect
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^account/', include('apps.account.urls')),
  url(r'^instance/', include('apps.instance.urls')),
  url(r'^installationdisk/', include('apps.installationdisk.urls')),
  url(r'^storagepool/', include('apps.storagepool.urls')),
  url(r'^hypervisor/', include('apps.hypervisor.urls')),
  url(r'^admin/', include(admin.site.urls)),
  url(r'^messages/', include('persistent_messages.urls')),
  url(r'^$', lambda x: HttpResponseRedirect('/account/')),
)

urlpatterns += staticfiles_urlpatterns()
