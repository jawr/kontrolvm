from django import forms
from apps.instance.models import InstanceTask
from apps.storagepool.models import StoragePool

class InstanceTaskForm(forms.ModelForm):
  storagepool = forms.ModelChoiceField(queryset=StoragePool.objects.filter(status=2))
  class Meta:
    model = InstanceTask
    exclude = ('name', 'creator', 'updated', 'created', 'volume',
      'status', 'state', 'message', 'task_id', 'percent', 'disk',)
