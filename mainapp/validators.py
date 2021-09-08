from datetime import datetime

import mainapp.models as models


def check_project_id(*, user_id_field_name='user_id'):
    def check_f(instance, attribute, value):
        if not models.Project.objects.id_is_valid(value):
            raise ValueError(attribute.name + ' is not valid!')

        user_id = getattr(instance, user_id_field_name)
        if not models.Project.objects.user_is_project_member(value, user_id):
            raise ValueError("User doesn't have access to project!")

    return check_f


def check_performer_id(*, project_id_field_name='project_id'):
    def check_f(instance, attribute, value):
        project_id = getattr(instance, project_id_field_name)
        project = models.Project.objects.by_id_or_none(project_id)
        if project is None or value not in project.members.values_list('id', flat=True):
            raise ValueError(attribute.name + ' is not valid!')

    return check_f


def check_group_id(*, project_id_field_name='project_id'):
    def check_f(instance, attribute, value):
        if not models.TaskGroup.objects.id_is_valid(value):
            raise ValueError(attribute.name + ' is not valid!')

        project_id = getattr(instance, project_id_field_name)
        if not models.Project.objects.task_group_belongs_to_project(project_id, value):
            raise ValueError(attribute.name + ' is not part of Project(id=' + project_id + ')!')

    return check_f


def check_task_id(*, project_id_field_name='project_id'):
    def check_f(instance, attribute, value):
        if not models.Task.objects.id_is_valid(value):
            raise ValueError(attribute.name + ' is not valid!')

        project_id = getattr(instance, project_id_field_name)
        if not models.Project.objects.task_belongs_to_project(project_id, value):
            raise ValueError(attribute.name + ' is not part of Project(id=' + project_id + ')!')

    return check_f


def check_task_name_free(*, project_id_field_name='project_id'):
    def check_f(instance, attribute, value):
        project_id = getattr(instance, project_id_field_name)
        names = models.Task.objects.get_task_names_in_project(project_id)
        if value in names or len(value) == 0:
            raise ValueError(attribute.name + ' is not valid')

    return check_f


def check_task_position(*, group_id_field_name='group_id'):
    def check_f(instance, attribute, value):
        group_id = getattr(instance, group_id_field_name)
        group = models.TaskGroup.objects.by_id_or_none(group_id)
        n = group.tasks.count()
        if not 0 <= value <= n:
            raise ValueError(attribute.name + ' is not valid!\n0 <= ' + attribute.name + ' <= ' + str(n) + ' expected!')

    return check_f


def check_task_group_position(*, project_id_field_name='project_id'):
    def check_f(instance, attribute, value):
        project_id = getattr(instance, project_id_field_name)
        n = models.TaskGroup.objects.number_in_project(project_id)
        if not 0 <= value < n:
            raise ValueError(attribute.name + ' is not valid!\n0 <= ' + attribute.name + ' <= ' + str(n) + ' expected!')

    return check_f


def check_task_group_name_free(*, project_id_field_name='project_id'):
    def check_f(instance, attribute, value):
        project_id = getattr(instance, project_id_field_name)
        if value in models.Project.objects.by_id_or_none(project_id).task_groups.values('name'):
            raise ValueError(attribute.name + ' is not valid!')

    return check_f


def check_time_in_future(*, time_now=None):
    if time_now is None:
        time_now = datetime.now()

    def check_f(instance, attribute, value):
        if time_now > value:
            raise ValueError(attribute.name + ' is not valid!')

    return check_f
