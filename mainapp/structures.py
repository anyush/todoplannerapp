import attr

import mainapp.validators as validators


@attr.s
class ProjectStructure(object):
    user_id = attr.ib(validator=attr.validators.instance_of(int))
    project_id = attr.ib(validator=(attr.validators.instance_of(int),
                                    validators.check_project_id()))


@attr.s
class TaskGroupCreateStructure(ProjectStructure):
    name = attr.ib(validator=(attr.validators.instance_of(str),
                              validators.check_task_group_name_free()))
    color = attr.ib(validator=(attr.validators.matches_re(regex=r'^#[0-9a-fA-F]{6}$')))
    task_color = attr.ib(validator=(attr.validators.matches_re(regex=r'^#[0-9a-fA-F]{6}$')))


@attr.s
class TaskGroupModifyStructure(TaskGroupCreateStructure):
    group_id = attr.ib(validator=(attr.validators.instance_of(int),
                                  validators.check_group_id()))


@attr.s
class TaskGroupMoveStructure(ProjectStructure):
    group_id = attr.ib(validator=(attr.validators.instance_of(int),
                                  validators.check_group_id()))
    new_pos = attr.ib(validator=(attr.validators.instance_of(int),
                                 validators.check_task_group_position()))


@attr.s
class TaskGroupDeleteStructure(ProjectStructure):
    group_id = attr.ib(validator=(attr.validators.instance_of(int),
                                  validators.check_group_id()))


@attr.s
class TaskMoveStructure(ProjectStructure):
    task_id = attr.ib(validator=(attr.validators.instance_of(int),
                                 validators.check_task_id()))
    new_group_id = attr.ib(validator=(attr.validators.instance_of(int),
                                      validators.check_group_id()))
    new_pos = attr.ib(validator=(attr.validators.instance_of(int),
                                 validators.check_task_position(group_id_field_name='new_group_id')))
