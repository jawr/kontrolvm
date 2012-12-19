from django import forms
from apps.volume.models import Volume

class VolumeForm(forms.ModelForm):
  class Meta:
    model = Volume
    exclude = ('allocated',)
