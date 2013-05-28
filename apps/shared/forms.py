from django import forms
from apps.shared.models import Size

class SizeForm(forms.Form):
  #size = forms.ModelChoiceField(queryset=Size.objects.all().order_by('size'), label="", help_text="")
  size = forms.ModelChoiceField(queryset=Size.objects.all(), label="", help_text="")
