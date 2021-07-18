from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Tag(models.Model):
    name = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)


class Project(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(User, on_delete=models.PROTECT, related_name='managed_projects')
    members = models.ManyToManyField(User, related_name='projects')
    tags = models.ManyToManyField(Tag, blank=True)


class Task(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    creation_time = models.DateTimeField()
    deadline_time = models.DateTimeField(blank=True)
    state = models.CharField(max_length=20)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='created_tasks')
    performers = models.ManyToManyField(User, related_name='performed_tasks', blank=True)
    tags = models.ManyToManyField(Tag, blank=True)
