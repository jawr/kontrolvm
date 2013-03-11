from django import forms

class LoginForm(forms.Form):
  username = forms.EmailField(max_length=200, required=True)
  password = forms.CharField(max_length=200, widget=forms.PasswordInput(), required=True)

class AddUserForm(forms.Form):
  email = forms.EmailField(max_length=200, required=True)
  email_check = forms.EmailField(max_length=200, required=True, label="Verify Email")
