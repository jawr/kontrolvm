from django import forms
from apps.instance.models import InstanceTask, InstanceCloneTask
from apps.storagepool.models import StoragePool
from apps.instance.models import Instance
from django.db.models import Q

class InstanceCloneTaskForm(forms.ModelForm):
  base = forms.ModelChoiceField(
    queryset=Instance.objects.filter(Q(status=5)&Q(is_base=True)))
  class Meta:
    model = InstanceCloneTask
    exclude = ('name', 'creator', 'updated', 'created', 'task_id',
      'percent', 'message', 'state')

class InstanceTaskForm(forms.ModelForm):
  storagepool = forms.ModelChoiceField(queryset=StoragePool.objects.filter(status=2))
  class Meta:
    model = InstanceTask
    exclude = ('name', 'creator', 'updated', 'created', 'volume',
      'status', 'state', 'message', 'task_id', 'percent', 'disk',)
