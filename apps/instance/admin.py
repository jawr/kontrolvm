from django.contrib import admin
from apps.instance.models import Instance, InstanceTask, InstanceCloneTask

admin.site.register(Instance)
admin.site.register(InstanceTask)
admin.site.register(InstanceCloneTask)
