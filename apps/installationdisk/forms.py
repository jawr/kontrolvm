from django import forms
from apps.installationdisk.models import InstallationDiskTask

class InstallationDiskTaskForm(forms.ModelForm):
  class Meta:
    model = InstallationDiskTask
    exclude = ('filename', 'task_id', 'total_bytes_dl', 'total_bytes', 
      'percent', 'state', 'user',)

class InstallationDisksForm(forms.Form):
  installation_disk = forms.ModelChoiceField(
    queryset=[],
    label='',
    required=False)
  
  def __init__(self, instance, *args, **kwargs):
    super(InstallationDisksForm, self).__init__(*args, **kwargs)
    self.fields['installation_disk'].initial = instance.disk
    self.fields['installation_disk'].queryset = instance.volume.storagepool.hypervisor.installationdisk_set.all()
