from django import forms
from apps.instance.models import InstanceTask

class InstanceTaskForm(forms.ModelForm):
  class Meta:
    model = InstanceTask
    exclude = ('name', 'creator', 'updated', 'created', 'volume',
      'status', 'state', 'message', 'task_id', 'percent',)
