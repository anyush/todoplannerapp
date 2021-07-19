from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .forms import CustomRegistrationForm, ProjectCreationForm
from .models import Project

# Create your views here.


def signup(request):
    if request.method == 'POST':
        form = CustomRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('')
    else:
        form = CustomRegistrationForm()
    return render(request, 'registration/signup.html', {'form': form})


def homepage(request):
    if request.user.is_authenticated:
        return HttpResponse(f'User: {request.user.username}')
    return HttpResponse("You're not logged in!")


@login_required
def project_page(request, project_id):
    if request.user.projects.filter(id=project_id).exists():
        project = Project.objects.filter(id=project_id).first()
        return render(request, 'project/project_about.html', context={'project': project})
    return redirect('')


@login_required
def project_creation(request):
    if request.method == 'POST':
        form = ProjectCreationForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.manager = request.user
            project.save()
            return redirect(f'/projects/{project.id}/')
    else:
        form = ProjectCreationForm(initial={'manager': request.user})
    return render(request, 'project/create_project.html', context={'form': form})
