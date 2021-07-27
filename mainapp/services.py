from django.contrib.auth import login
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
