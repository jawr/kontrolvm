from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
  url(r'^account/', include('apps.account.urls')),
  url(r'^hypervisor/', include('apps.hypervisor.urls')),
  url(r'^admin/', include(admin.site.urls)),
  url(r'^messages/', include('persistent_messages.urls')),
)

urlpatterns += staticfiles_urlpatterns()
