from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms.widgets import PasswordInput, TextInput, Textarea, SelectMultiple
from django.forms import ModelForm

import mainapp.models as models


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
    tags_choices = ((tag, tag.name) for tag in models.Tag.objects.all())
    tags = forms.MultipleChoiceField(widget=SelectMultiple(attrs={'class': 'form_field'}), choices=tags_choices,
                                     required=False)

    class Meta:
        model = models.Project
        fields = ('name', 'description', 'members', 'tags')


class TaskGroupForm(ModelForm):
    DEFAULT_COLOR = '#93b3db'
    DEFAULT_TASK_COLOR = '#ebd06e'

    name = forms.CharField(widget=TextInput(attrs={'id': 'modifiableGroupName', 'class': 'modalField'}))
    color = forms.CharField(widget=forms.TextInput(attrs={'id': 'modifiableGroupColor', 'type': 'color',
                                                          'default': DEFAULT_COLOR}),
                            initial=DEFAULT_COLOR)
    task_color = forms.CharField(widget=forms.TextInput(attrs={'id': 'modifiableGroupTaskColor', 'type': 'color',
                                                               'default': DEFAULT_TASK_COLOR}),
                                 initial=DEFAULT_TASK_COLOR)
    tags_choices = ((tag, tag.name) for tag in models.Tag.objects.all())
    tags = forms.MultipleChoiceField(widget=SelectMultiple(attrs={'class': 'modalField'}), choices=tags_choices,
                                     required=False)

    class Meta:
        model = models.TaskGroup
        fields = ('name', 'color', 'task_color', 'tags')


class TaskForm(ModelForm):
    name = forms.CharField(widget=TextInput(attrs={'id': 'modifiableTaskName',
                                                   'class': 'modalField'}))
    description = forms.CharField(widget=Textarea(attrs={'id': 'modifiableTaskDescription',
                                                         'class': 'modalField'}))
    deadline_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'id': 'modifiableTaskDeadlineHidden',
                                                                          'hidden': 'hidden'}),
                                        required=False)
    performers_choices = ((usr.id, usr.username) for usr in models.User.objects.all())
    performers = forms.MultipleChoiceField(widget=SelectMultiple(attrs={'id': 'modifiableTaskPerformers',
                                                                        'class': 'modalField'}),
                                           choices=performers_choices,
                                           required=False)
    tags_choices = ((tag, tag.name) for tag in models.Tag.objects.all())
    tags = forms.MultipleChoiceField(widget=SelectMultiple(attrs={'id': 'modifiableTaskTags',
                                                                  'class': 'modalField'}),
                                     choices=tags_choices,
                                     required=False)

    class Meta:
        model = models.Task
        fields = ('name', 'description', 'deadline_time', 'performers', 'tags')
