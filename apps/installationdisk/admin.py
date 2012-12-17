from django.contrib import admin
from apps.installationdisk.models import InstallationDisk, InstallationDiskTask

admin.site.register(InstallationDisk)
admin.site.register(InstallationDiskTask)
