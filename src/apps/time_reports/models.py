import datetime
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.urls.base import reverse
from django.utils.html import format_html
from django.shortcuts import  redirect
from djmoney.models.fields import MoneyField
from PIL import Image
from ..base.models import unique_slugify

class TimeReport(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    start_date = models.DateField()
    # status = models.CharField(max_length=20, default='draft')
    # is_submitted = models.BooleanField(default=False)
    # is_approved = models.BooleanField(default=False)
    # is_paid = models.BooleanField(default=False)

    def __str__(self):
        return self.employee.user.first_name + ' ' + self.employee.user.last_name + ' - ' + self.start_date.strftime('%Y.%m')

class ProjectTime(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    time_report = models.ForeignKey('TimeReport', on_delete=models.CASCADE)

class ProjectTimeDay(models.Model):
    project_time = models.ForeignKey('ProjectTime', on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    
class ProjectExpense(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    time_report = models.ForeignKey('TimeReport', on_delete=models.CASCADE)

class BusinessTrip(models.Model):
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    time_report = models.ForeignKey('TimeReport', on_delete=models.CASCADE)
    is_international = models.BooleanField(default=False)
    country = models.CharField(max_length=100, blank=True, null=True) # jako slownik czy moze tabela z krajami?
