from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
import json

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)


class ProjectManager(models.Manager):
    def id_is_valid(self, project_id):
        return self.filter(id=project_id).exists()

    def by_id_or_none(self, project_id):
        if self.id_is_valid(project_id):
            return self.get(id=project_id)
        return None

    def user_is_project_member(self, project_id, user_id):
        project = self.by_id_or_none(project_id)
        if project is not None:
            return project.members.filter(id=user_id).exists()
        return False

    def task_group_belongs_to_project(self, project_id, group_id):
        return self.filter(id=project_id, task_groups__id=group_id)

    def task_belongs_to_project(self, project_id, task_id):
        return self.filter(id=project_id, task_groups__tasks__id=task_id).exists()


class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_projects')
    members = models.ManyToManyField(User, related_name='projects')
    tags = models.ManyToManyField(Tag, blank=True)

    objects = ProjectManager()


class TaskGroupManager(models.Manager):
    def id_is_valid(self, group_id):
        return self.filter(id=group_id).exists()

    def by_id_or_none(self, group_id):
        if self.id_is_valid(group_id):
            return self.get(id=group_id)
        return None

    def by_project_id(self, project_id):
        return self.filter(project__id=project_id)

    def number_in_project(self, project_id):
        return self.by_project_id(project_id).count()

    def position_in_project_between(self, project_id, start, end):
        """
        Both start and end positions excluded
        """
        return self.by_project_id(project_id).filter(position__gt=start, position__lt=end)


class TaskGroup(models.Model):
    position = models.IntegerField()
    name = models.CharField(max_length=20)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='task_groups')
    color = models.CharField(max_length=10)
    task_color = models.CharField(max_length=10)
    tags = models.ManyToManyField(Tag, blank=True)

    objects = TaskGroupManager()

    def as_json(self):
        return json.dumps(
            {
                'id': self.id,
                'position': self.position,
                'name': self.name,
                'project_id': self.project.id,
                'color': self.color,
                'task_color': self.task_color,
                'tag_ids': tuple(self.tags.values('id'))
            }
        )


class TaskManager(models.Manager):
    def id_is_valid(self, task_id):
        return self.filter(id=task_id).exists()

    def by_id_or_none(self, task_id):
        if self.id_is_valid(task_id):
            return self.get(id=task_id)
        return None

    def by_group_id(self, group_id):
        return self.filter(task_group__id=group_id)

    def number_in_group(self, group_id):
        return self.by_group_id(group_id).count()

    def position_in_group_greater_than(self, group_id, gt):
        """
            'gt' position excluded
        """
        return self.by_group_id(group_id).filter(position__gt=gt)

    def get_task_names_in_project(self, project_id):
        return self.filter(task_group__project__id=project_id).values_list('name')


class Task(models.Model):
    position = models.IntegerField()
    name = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    task_group = models.ForeignKey(TaskGroup, on_delete=models.CASCADE, related_name='tasks')
    creation_time = models.DateTimeField(auto_now_add=True)
    deadline_time = models.DateTimeField(blank=True, null=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_tasks')
    performers = models.ManyToManyField(User, related_name='performed_tasks', blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    objects = TaskManager()

    def as_json(self):
        return json.dumps(
            {
                'id': self.id,
                'position': self.position,
                'name': self.name,
                'description': self.description,
                'task_group_id': self.task_group.id,
                'creation_time': self.creation_time,
                'deadline_time': self.deadline_time,
                'creator_id': self.creator.id,
                'performer_ids': tuple(self.performers.values('id')),
                'tag_ids': tuple(self.tags.values('id')),
            },
            cls=DjangoJSONEncoder
        )
