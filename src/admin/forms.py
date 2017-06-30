from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(widget=forms.PasswordInput)


class EditForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    passwordConfirm = forms.CharField(widget=forms.PasswordInput)
