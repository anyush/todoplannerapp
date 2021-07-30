from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from .forms import CustomRegistrationForm, ProjectCreationForm
import mainapp.services as services
import mainapp.decorators as decorators

# Create your views here.


def signup(request):
    if request.method == 'POST' and services.try_register_user(request):
        return redirect('')

    form = CustomRegistrationForm()
    return render(request, 'registration/signup.html', {'form': form})


def homepage(request):
    if request.user.is_authenticated:
        return HttpResponse(f'User: {request.user.username}')
    return HttpResponse("You're not logged in!")


@login_required
@decorators.project_id_is_valid
@decorators.user_is_project_member
def project_page(request, project_id):
    data = services.get_project_page_data(project_id)
    return render(request, 'project/project.html', context={'data': data})


@login_required
@decorators.project_id_is_valid
@decorators.user_is_project_member
@decorators.ajax_only
def project_page_move_col(request, project_id):
    if request.method == 'POST':
        services.change_task_group_position(request, project_id)
    return JsonResponse({})


@login_required
@decorators.project_id_is_valid
@decorators.user_is_project_member
@decorators.ajax_only
def project_page_move_task(request, project_id):
    if request.method == 'POST':
        services.change_task_position(request, project_id)
    return JsonResponse({})


@login_required
@decorators.project_id_is_valid
@decorators.user_is_project_member
def project_about(request, project_id):
    project = services.get_project_by_id(project_id)
    return render(request, 'project/project_about.html', context={'project': project})


@login_required
def project_creation(request):
    if request.method == 'POST':
        created, project_id = services.try_create_project(request)
        if created:
            return redirect(f'/projects/{project_id}/')

    form = ProjectCreationForm(initial={'manager': request.user})
    return render(request, 'project/create_project.html', context={'form': form})
