from django.shortcuts import redirect
from .models import Project
from functools import wraps


def project_id_is_valid(view_func):
    @wraps(view_func)
    def wrapper(request, project_id):
        if not Project.objects.filter(id=project_id).exists():
            return redirect('')
        return view_func(request, project_id)
    return wrapper


def user_is_project_member(view_func) -> bool:
    @wraps(view_func)
    def wrapper(request, project_id):
        if not request.user.projects.filter(id=project_id).exists():
            return redirect('')
        return view_func(request, project_id)
    return wrapper
