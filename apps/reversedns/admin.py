from django.contrib import admin
from apps.reversedns.models import ReverseDNSRequest, ReverseDNS

admin.site.register(ReverseDNS)
admin.site.register(ReverseDNSRequest)
