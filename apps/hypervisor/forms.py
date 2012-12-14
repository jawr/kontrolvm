from django import forms
from apps.hypervisor.models import Hypervisor

class HypervisorForm(forms.ModelForm):
  class Meta:
    model = Hypervisor
    exclude = ('status',)
