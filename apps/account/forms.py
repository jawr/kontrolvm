from django import forms

class LoginForm(forms.Form):
  username = forms.EmailField(max_length=200, required=True)
  password = forms.CharField(max_length=200, widget=forms.PasswordInput(), required=True)
