import attr
from datetime import datetime

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
class TaskCreateStructure(ProjectStructure):
    name = attr.ib(validator=(attr.validators.instance_of(str),
                              validators.check_task_name_free()))
    description = attr.ib(validator=attr.validators.instance_of(str))
    group_id = attr.ib(validator=(attr.validators.instance_of(int),
                                  validators.check_group_id()))
    deadline_validator = attr.validators.optional(
        attr.validators.and_(attr.validators.instance_of(datetime),
                             validators.check_time_in_future()))
    deadline_time = attr.ib(default=None,
                            validator=deadline_validator)
    performers_member_validator = attr.validators.and_(attr.validators.instance_of(int),
                                                       validators.check_performer_id())
    performers = attr.ib(default=None,
                         validator=attr.validators.deep_iterable(member_validator=performers_member_validator))


@attr.s
class TaskMoveStructure(ProjectStructure):
    task_id = attr.ib(validator=(attr.validators.instance_of(int),
                                 validators.check_task_id()))
    new_group_id = attr.ib(validator=(attr.validators.instance_of(int),
                                      validators.check_group_id()))
    new_pos = attr.ib(validator=(attr.validators.instance_of(int),
                                 validators.check_task_position(group_id_field_name='new_group_id')))
