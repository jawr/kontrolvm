from django import forms

class LoginForm(forms.Form):
  username = forms.EmailField(max_length=200, required=True)
  password = forms.CharField(max_length=200, widget=forms.PasswordInput(), required=True)

class AddUserForm(forms.Form):
  email = forms.EmailField(max_length=200, required=True)
  email_check = forms.EmailField(max_length=200, required=True, label="Verify Email")

class UserInitForm(forms.Form):
  keep_password = forms.BooleanField(required=False, label="Keep randomly generated password")

class UserNameForm(forms.Form):
  first_name = forms.CharField(max_length=200, required=True)
  last_name = forms.CharField(max_length=200, required=True)

class UserPasswordForm(forms.Form):
  password = forms.CharField(max_length=200, widget=forms.PasswordInput(), required=True)
  password_check = forms.CharField(max_length=200, widget=forms.PasswordInput(), required=True)
