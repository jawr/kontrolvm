from django import forms
from apps.network.models import Network, InstanceNetwork

class NetworkForm(forms.ModelForm):
  class Meta:
    model = Network

class InstanceNetworkForm(forms.ModelForm):
  class Meta:
    model = InstanceNetwork

class NetworkListForm(forms.Form):
  network = forms.ModelChoiceField(queryset=Network.objects.all())

class IPForm(forms.Form):
  ip = forms.ChoiceField(label='IP Address')
  network = forms.IntegerField(widget=forms.HiddenInput())

  def clean_model_instance(self):
    pk =  self.cleaned_data['model_instance']
    if not pk:
      raise forms.ValidationError()
    try:
      instance = Network.objects.get(pk=pk)
    except Network.DoesNotExist:
      raise forms.ValidationError()
    return instance

