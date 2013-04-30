from django.conf.urls.defaults import *
from django.views.generic import TemplateView                                   

urlpatterns = patterns('apps.account.views',
  url(r'^login', 'account_login'),
  url(r'^logout', 'account_logout'),
  url(r'^$', 'index'),
  url(r'^admin', 'admin'),
  url(r'^add', 'add'),
  url(r'^success', TemplateView.as_view(template_name='account/success.html')),
)
