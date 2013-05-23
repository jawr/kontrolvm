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
