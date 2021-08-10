from django.contrib.auth import login
import json

import mainapp.forms as forms
import mainapp.models as models


def try_register_user(request) -> bool:
    form = forms.CustomRegistrationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return True
    return False


def try_create_project(request) -> (bool, int):
    form = forms.ProjectCreationForm(request.POST)
    if form.is_valid():
        project = form.save(commit=False)
        project.manager = request.user
        project.save()
        return True
    return False


def get_project_page_data(project_id) -> tuple:
    return tuple((group, tuple(models.Task.objects.by_group_id(group.id).order_by('position')))
                 for group in models.TaskGroup.objects.by_project_id(project_id).order_by('position'))


def values_between(values, start, end) -> bool:
    """
    Checks if all values from 'values' are greater than 'start' and less than 'end'
    """
    for value in values:
        if not start < value < end:
            return False
    return True
