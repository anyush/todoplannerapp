from django.contrib.auth import login
import json

import mainapp.forms as forms
import mainapp.models as models


def try_register_user(request) -> (bool, int):
    form = forms.CustomRegistrationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return True, user.id
    return False, -1


def try_create_project(request) -> (bool, int):
    form = forms.ProjectCreationForm(request.POST)
    if form.is_valid():
        project = form.save(commit=False)
        project.manager = request.user
        project.save()
        return True, project.id
    return False, -1


def try_create_task_group(request, project_id) -> (bool, int):
    form = forms.TaskGroupCreationForm(request.POST, project_id=project_id)
    project = models.Project.objects.by_id_or_none(project_id)
    if form.is_valid() and project_id is not None:
        group = form.save(commit=False)
        group.project = project
        group.position = models.TaskGroup.objects.number_in_project(project_id)
        group.save()
        return True, group.id
    return False, -1


def get_project_page_data(project_id) -> str:
    project_data = tuple(
        (
            group.as_json(),
            tuple(
                task.as_json()
                for task in models.Task.objects.by_group_id(group.id).order_by('position')
            )
        )
        for group in models.TaskGroup.objects.by_project_id(project_id).order_by('position')
    )

    return json.dumps(project_data)


def get_missing_task_groups(project_id, group_ids) -> tuple:
    missing_groups = models.TaskGroup.objects.by_project_id(project_id).exclude(id__in=group_ids)
    return tuple(missing_groups)


def values_between(values, start, end) -> bool:
    """
    Checks if all values from 'values' are greater than 'start' and less than 'end'
    """
    for value in values:
        if not start < value < end:
            return False
    return True
