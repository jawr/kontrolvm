from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.http import HttpResponseRedirect
from django.contrib import admin
from dajaxice.core import dajaxice_autodiscover, dajaxice_config

admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns('',
  url(r'^network/', include('apps.network.urls')),
  url(r'^account/', include('apps.account.urls')),
  url(r'^instance/', include('apps.instance.urls')),
  url(r'^installationdisk/', include('apps.installationdisk.urls')),
  url(r'^storagepool/', include('apps.storagepool.urls')),
  url(r'^hypervisor/', include('apps.hypervisor.urls')),
  url(r'^snapshot/', include('apps.snapshot.urls')),                            
  url(r'^admin/', include(admin.site.urls)),
  url(r'^messages/', include('persistent_messages.urls')),
  url(r'^reversedns/', include('apps.reversedns.urls')),
  url(r'^$', lambda x: HttpResponseRedirect('/account/')),
  url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

urlpatterns += staticfiles_urlpatterns()
