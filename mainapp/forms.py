from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput


class CustomAuthForm(AuthenticationForm):
    username = forms.CharField(widget=TextInput(attrs={'placeholder': '👩‍💻 Enter Username',
                                                       'class': 'form_field'}))
    password = forms.CharField(widget=PasswordInput(attrs={'placeholder': '🔒 Enter Password',
                                                           'class': 'form_field'}))


class CustomRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=TextInput(attrs={'placeholder': '👩‍💻 Enter Username',
                                                       'class': 'form_field'}))
    password1 = forms.CharField(widget=PasswordInput(attrs={'placeholder': '🔒 Enter Password',
                                                            'class': 'form_field'}))
    password2 = forms.CharField(widget=PasswordInput(attrs={'placeholder': '🔒 Enter Password',
                                                            'class': 'form_field'}))

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2')
