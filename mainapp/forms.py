from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput, Textarea, SelectMultiple
from django.forms import ModelForm
from .models import Project, User, Tag


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


class ProjectCreationForm(ModelForm):
    name = forms.CharField(widget=TextInput(attrs={'class': 'form_field'}))
    description = forms.CharField(widget=Textarea(attrs={'class': 'form_field'}))
    members_choices = ((user, user.username) for user in User.objects.all())
    members = forms.MultipleChoiceField(widget=SelectMultiple(attrs={'class': 'form_field'}), choices=members_choices,
                                        required=False)
    tags_choices = ((tag, tag.name) for tag in Tag.objects.all())
    tags = forms.MultipleChoiceField(widget=SelectMultiple(attrs={'class': 'form_field'}), choices=tags_choices,
                                     required=False)

    class Meta:
        model = Project
        fields = ('name', 'description', 'members', 'tags')
