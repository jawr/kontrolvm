from django import forms
from apps.installationdisk.models import InstallationDiskTask

class InstallationDiskTaskForm(forms.ModelForm):
  class Meta:
    model = InstallationDiskTask
    exclude = ('filename', 'task_id', 'total_bytes_dl', 'total_bytes', 
      'percent', 'state', 'user',)

class InstallationDisksForm(forms.Form):
  installation_disk = forms.ModelChoiceField(queryset=[])
  
  def __init__(self, hypervisor, *args, **kwargs):
    super(InstallationDisksForm, self).__init__(*args, **kwargs)
    self.fields['installation_disk'].queryset = hypervisor.installationdisk_set.all()
