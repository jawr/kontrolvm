from django import forms

class ReverseDNSRequestForm(forms.Form):
  rdns = forms.CharField(max_length=255, label="rDNS")
