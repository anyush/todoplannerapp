from django.contrib import admin
import mainapp.models as models

# Register your models here.


admin.site.register(models.Project)
admin.site.register(models.TaskGroup)
admin.site.register(models.Task)
