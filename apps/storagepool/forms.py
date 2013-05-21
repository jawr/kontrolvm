from django import forms
from apps.storagepool.models import StoragePool

class StoragePoolForm(forms.ModelForm):
  class Meta:
    model = StoragePool
    exclude = ('status','allocated','available','percent','capacity')
