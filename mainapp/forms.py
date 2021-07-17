from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'placeholder': '👩‍💻 Enter Username'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder': '🔒 Enter Password'}))


class CustomRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=TextInput(attrs={'placeholder': '👩‍💻 Enter Username'}))
    password1 = forms.CharField(widget=PasswordInput(attrs={'placeholder': '🔒 Enter Password'}))
    password2 = forms.CharField(widget=PasswordInput(attrs={'placeholder': '🔒 Enter Password'}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
