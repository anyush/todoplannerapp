from django.contrib.auth import login
from django.db import transaction
from django.db.models import F
from django.db.models.query import QuerySet
from .forms import CustomRegistrationForm, ProjectCreationForm
from .models import Project, TaskGroup, Task
import json


def try_register_user(request) -> bool:
    form = CustomRegistrationForm(request.POST)
    if form.is_valid():
        user = form.save()
        login(request, user)
        return True
    return False


def try_create_project(request) -> (bool, int):
    form = ProjectCreationForm(request.POST)
    if form.is_valid():
        project = form.save(commit=False)
        project.manager = request.user
        project.save()
        return True
    return False


def project_id_is_valid(project_id) -> bool:
    return Project.objects.filter(id=project_id).exists()


def get_project_by_id(project_id) -> Project:
    if project_id_is_valid(project_id):
        return Project.objects.get(id=project_id)
    raise ValueError


def get_task_groups_by_project_id(project_id) -> QuerySet:
    return TaskGroup.objects.filter(project__id=project_id)


def get_tasks_by_group_id(task_group_id) -> QuerySet:
    return Task.objects.filter(task_group__id=task_group_id)


def user_is_project_member(request, project_id) -> bool:
    return request.user.projects.filter(id=project_id).exists()


def get_project_page_data(project_id) -> tuple:
    return tuple((group, tuple(get_tasks_by_group_id(group.id).order_by('position')))
                 for group in get_task_groups_by_project_id(project_id).order_by('position'))


def get_task_group_by_project_id_and_position(project_id, position) -> TaskGroup:
    return TaskGroup.objects.get(project__id=project_id, position=position)


def get_task_by_task_group_id_and_position(task_group_id, position) -> Task:
    return Task.objects.get(task_group__id=task_group_id, position=position)


def get_task_group_number_in_project(project_id) -> int:
    return TaskGroup.objects.filter(project__id=project_id).count()


def get_task_number_in_task_group(task_group_id) -> int:
    return Task.objects.filter(task_group__id=task_group_id).count()


@transaction.atomic
def change_task_group_position(request, project_id) -> bool:
    data = json.loads(request.body)
    old_pos = data['old_pos']
    new_pos = data['new_pos']
    task_group_number = get_task_group_number_in_project(project_id)
    if old_pos == new_pos or not 0 <= old_pos < task_group_number or not 0 <= new_pos < task_group_number:
        return False
    moved_task_group = get_task_group_by_project_id_and_position(project_id, old_pos)
    if old_pos < new_pos:
        TaskGroup.objects.filter(project__id=project_id, position__gt=old_pos, position__lte=new_pos)\
            .update(position=F('position')-1)
    else:
        TaskGroup.objects.filter(project__id=project_id, position__gte=new_pos, position__lt=old_pos)\
            .update(position=F('position')+1)
    moved_task_group.position = new_pos
    moved_task_group.save()
    return True


@transaction.atomic
def change_task_position(request, project_id) -> bool:
    data = json.loads(request.body)
    old_group_pos = data['old_group_pos']
    new_group_pos = data['new_group_pos']
    old_pos = data['old_pos']
    new_pos = data['new_pos']
    task_group_number = get_task_group_number_in_project(project_id)
    if (old_group_pos == new_group_pos and old_pos == new_pos) or not 0 <= old_group_pos < task_group_number or \
            not 0 <= new_group_pos < task_group_number:
        return False
    old_group = get_task_group_by_project_id_and_position(project_id, old_group_pos)
    new_group = get_task_group_by_project_id_and_position(project_id, new_group_pos)
    task_number_old_task_group = get_task_number_in_task_group(old_group.id)
    task_number_new_task_group = get_task_number_in_task_group(new_group.id)
    if not 0 <= old_pos < (task_number_old_task_group or 1) or not 0 <= new_pos < (task_number_new_task_group or 1):
        return False
    moved_task = get_task_by_task_group_id_and_position(old_group.id, old_pos)
    Task.objects.filter(task_group=old_group, position__gt=old_pos).update(position=F('position')-1)
    Task.objects.filter(task_group=new_group, position__gte=new_pos).update(position=F('position')+1)
    moved_task.task_group = new_group
    moved_task.position = new_pos
    moved_task.save()
    return True
