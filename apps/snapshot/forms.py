from django import forms
from apps.snapshot.models import Snapshot

class SnapshotForm(forms.Form):
  snapshot = forms.ModelChoiceField(
    queryset=[],
    label='',
    required=False)
  
  def __init__(self, instance, *args, **kwargs):
    super(SnapshotForm, self).__init__(*args, **kwargs)
    self.fields['snapshot'].queryset = Snapshot.objects.filter(instance=instance)
