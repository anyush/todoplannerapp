from django.contrib.auth import login
from django.db import transaction
from django.db.models import F
from .forms import CustomRegistrationForm, ProjectCreationForm
from .models import Project, TaskGroup, Task


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


def project_id_is_valid(project_id):
    return Project.objects.filter(id=project_id).exists()


def get_project_by_id(project_id) -> Project:
    if project_id_is_valid(project_id):
        return Project.objects.get(id=project_id)
    raise ValueError


def user_is_project_member(request, project_id) -> bool:
    return request.user.projects.filter(id=project_id).exists()


def get_project_task_group_style(task_group) -> str:
    return "background-color: " + task_group.color


def get_project_task_style(task_group) -> str:
    return "background-color: " + task_group.task_color


def get_project_page_data(project_id) -> tuple:
    return tuple((group.name,
                  tuple(Task.objects.filter(task_group=group.id).order_by('position')),
                  get_project_task_group_style(group),
                  get_project_task_style(group))
                 for group in TaskGroup.objects.filter(project_id=project_id).order_by('position'))


@transaction.atomic
def change_task_group_position(project_id, old_pos, new_pos) -> bool:
    if old_pos == new_pos or new_pos < 0 or new_pos > TaskGroup.objects.filter(project_id=project_id).count():
        return False
    moved_task = TaskGroup.objects.get(project=project_id, position=old_pos)
    if old_pos < new_pos:
        TaskGroup.objects.filter(project__id=project_id, position__gt=old_pos, position__lte=new_pos)\
            .update(position=F('position')-1)
    else:
        TaskGroup.objects.filter(project__id=project_id, position__gte=new_pos, position__lt=old_pos)\
            .update(position=F('position')+1)
    moved_task.position = new_pos
    moved_task.save()
    return True
