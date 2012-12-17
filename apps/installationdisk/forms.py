from django import forms
from apps.installationdisk.models import InstallationDiskTask

class InstallationDiskTaskForm(forms.ModelForm):
  class Meta:
    model = InstallationDiskTask
    exclude = ('filename', 'task_id',)
