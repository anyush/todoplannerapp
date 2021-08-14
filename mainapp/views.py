from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.urls import reverse

import mainapp.services as services
import mainapp.decorators as decorators
import mainapp.models as models
import mainapp.forms as forms

# Create your views here.


def signup(request):
    if request.method == 'POST' and services.try_register_user(request)[0]:
        return redirect('')

    form = forms.CustomRegistrationForm()
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
    return render(request, 'project/project.html', context={'data': data, 'project_id': project_id})


@login_required
@decorators.project_id_is_valid
@decorators.user_is_project_member
def project_about(request, project_id):
    project = models.Project.objects.by_id_or_none(project_id)
    return render(request, 'project/project_about.html', context={'project': project})


@login_required
def project_creation(request):
    if request.method == 'POST':
        created, project_id = services.try_create_project(request)
        if created:
            return redirect(f'/projects/{project_id}/')

    form = forms.ProjectCreationForm(initial={'manager': request.user})
    return render(request, 'project/create_project.html', context={'form': form})


@login_required
@decorators.project_id_is_valid
@decorators.user_is_project_member
def task_group_creation(request, project_id):
    if request.method == 'POST':
        created, task_group_id = services.try_create_task_group(request, project_id)
        if created:
            return redirect(reverse('project_page', kwargs={'project_id': project_id}))

    form = forms.TaskGroupCreationForm(project_id=project_id)
    return render(request, 'project/new_task_group.html', context={'form': form})
