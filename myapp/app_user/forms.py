from django import forms
from django.contrib.auth import forms as auth_forms
from myapp.app_user.models import User


class LoginForm(auth_forms.AuthenticationForm):
    username = auth_forms.UsernameField(max_length=255,
        widget=forms.TextInput(attrs={"class": "form-control",
                                      "placeholder": "login"}))

    password = forms.CharField(max_length=255,
        widget=forms.PasswordInput(attrs={"class": "form-control",
                                          "placeholder": "password"}))

    class Meta:
        model = User
        fields = ['username', 'password']
