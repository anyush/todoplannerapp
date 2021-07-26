from django.contrib import admin
from .models import Project, TaskGroup, Task

# Register your models here.


admin.site.register(Project)
admin.site.register(TaskGroup)
admin.site.register(Task)
