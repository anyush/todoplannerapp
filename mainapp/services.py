from django.contrib.auth import login
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
import json

import mainapp.forms as forms
import mainapp.models as models
import mainapp.structures as structures


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


def create_task_group(context_struct) -> None:
    models.TaskGroup.objects.create(
        position=models.TaskGroup.objects.number_in_project(context_struct.project_id),
        project=models.Project.objects.by_id_or_none(context_struct.project_id),
        name=context_struct.name,
        color=context_struct.color,
        task_color=context_struct.task_color
    )


def modify_task_group(context_struct) -> None:
    group = models.TaskGroup.objects.by_id_or_none(context_struct.group_id)
    group.name = context_struct.name
    group.color = context_struct.color
    group.task_color = context_struct.task_color
    group.save()


def move_task_group(context_struct) -> None:
    moved_group = models.TaskGroup.objects.by_id_or_none(context_struct.group_id)

    old_pos = moved_group.position
    new_pos = context_struct.new_pos
    if old_pos == new_pos:
        return

    with transaction.atomic():
        if old_pos < new_pos:
            affected_groups = models.TaskGroup.objects\
                .position_in_project_between(context_struct.project_id, old_pos, new_pos + 1)
            affected_groups.update(position=F('position') - 1)
        else:
            affected_groups = models.TaskGroup.objects\
                .position_in_project_between(context_struct.project_id, new_pos - 1, old_pos)
            affected_groups.update(position=F('position') + 1)

        moved_group.position = new_pos
        moved_group.save()


def delete_task_group(context_struct) -> None:
    deleted_group = models.TaskGroup.objects.by_id_or_none(context_struct.group_id)
    deleted_group.delete()


def create_task(context_struct: structures.TaskCreateStructure) -> (int, bool):
    performers = (User.objects.get(id=perf_id) for perf_id in context_struct.performers) \
        if context_struct.performers is not None else None
    task = models.Task.objects.create(
        position=models.Task.objects.number_in_group(context_struct.group_id),
        name=context_struct.name,
        description=context_struct.description if context_struct.description is not None else '',
        task_group=models.TaskGroup.objects.by_id_or_none(context_struct.group_id),
        deadline_time=context_struct.deadline_time,
        creator=User.objects.get(id=context_struct.user_id),
    )

    if performers is not None:
        task.performers.set(performers)
        task.save()

    return task.id, True


def move_task(context_struct) -> None:
    moved_task = models.Task.objects.by_id_or_none(context_struct.task_id)

    old_group = moved_task.task_group
    old_pos = moved_task.position

    new_group = models.TaskGroup.objects.by_id_or_none(context_struct.new_group_id)
    new_pos = context_struct.new_pos

    if old_group == new_group and old_pos == new_pos:
        return

    with transaction.atomic():
        models.Task.objects.position_in_group_greater_than(old_group.id, old_pos)\
            .update(position=F('position') - 1)
        models.Task.objects.position_in_group_greater_than(new_group.id, new_pos-1)\
            .update(position=F('position') + 1)
        moved_task.task_group = new_group
        moved_task.position = new_pos
        moved_task.save()


def delete_task(context_struct: structures.TaskDeleteStructure) -> bool:
    deleted_task = models.Task.objects.by_id_or_none(context_struct.task_id)
    deleted_task.delete()
    return True
