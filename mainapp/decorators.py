from django.shortcuts import redirect
from functools import wraps

import mainapp.models as models


BAD_REQUEST_URL = ''  # url to redirect if bad request received


def project_id_is_valid(view_func):
    """
    Run view_func if project id given via url is valid, redirect to BAD_REQUEST_URL otherwise.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        project_id = kwargs.get('project_id', -1)
        if models.Project.objects.id_is_valid(project_id):
            return view_func(request, *args, **kwargs)
        return redirect(BAD_REQUEST_URL)
    return wrapper


def user_is_project_member(view_func):
    """
    Run view_func if user has access to project with project.id given via url, redirect to BAD_REQUEST_URL otherwise.
    If project doesn't exist user will be redirected to BAD_REQUEST_URL, but @project_is_valid is advised to use.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        project_id = kwargs.get('project_id', -1)
        if models.Project.objects.user_is_project_member(project_id, request.user.id):
            return view_func(request, *args, **kwargs)
        return redirect(BAD_REQUEST_URL)
    return wrapper


def task_group_id_is_valid(view_func):
    """
    Run view_func if group id given via url is valid, redirect to BAD_REQUEST_URL otherwise.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        group_id = kwargs.get('group_id', -1)
        if models.TaskGroup.objects.id_is_valid(group_id):
            return view_func(request, *args, **kwargs)
        return redirect(BAD_REQUEST_URL)
    return wrapper


def user_has_access_to_task_group(view_func):
    """
    Run view_func if user has access to project which group given via url belongs to,
    redirect to BAD_REQUEST_URL otherwise.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        group_id = kwargs.get('group_id', -1)
        group = models.TaskGroup.objects.by_id_or_none(group_id)
        if group is None:
            return redirect(BAD_REQUEST_URL)

        if models.Project.objects.user_is_project_member(group.project.id, request.user.id):
            return view_func(request, group_id, *args, **kwargs)
        return redirect(BAD_REQUEST_URL)
    return wrapper


def ajax_only(view_func):
    """
    Run view_func if ajax request was received, redirect to BAD_REQUEST_URL otherwise.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.is_ajax():
            return view_func(request, *args, **kwargs)
        return redirect(BAD_REQUEST_URL)
    return wrapper
