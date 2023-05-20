from django.contrib import admin
from .models import TimeReport, ProjectRecord, ProjectTime
# Register your models here.
admin.site.register(TimeReport)
admin.site.register(ProjectRecord)
admin.site.register(ProjectTime)