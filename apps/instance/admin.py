from django.contrib import admin
from apps.instance.models import Instance, InstanceTask

admin.site.register(Instance)
admin.site.register(InstanceTask)
