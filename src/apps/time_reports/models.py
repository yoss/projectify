import calendar
import datetime
from typing import Any, Dict
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import models
from django.urls.base import reverse
from django.utils.html import format_html
from django.shortcuts import  redirect
from djmoney.models.fields import MoneyField, Money
from PIL import Image
from ..base.models import unique_slugify
from django.core.validators import MaxValueValidator, MinValueValidator 
from django.db.models import Sum, Q

DRAFT = 'draft'
SUBMITTED = 'submitted'
APPROVED = 'approved'
REJECTED = 'rejected'

STATUS_CHOICES = [
    (DRAFT, 'Draft'),
    (SUBMITTED, 'Submitted'),
    (APPROVED, 'Approved'),
    (REJECTED, 'Rejected'),
]

class TimeReport(models.Model):
    employee = models.ForeignKey('employees.Employee', on_delete=models.CASCADE)
    start_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    total_hours = models.PositiveSmallIntegerField(default=0)
    total_amount_net = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN', default=0)
    total_amount_gross = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN', default=0)

    def __str__(self):
        return self.employee.user.first_name + ' ' + self.employee.user.last_name + ' - ' + self.start_date.strftime('%B %Y')
    
    def get_absolute_url(self): return reverse('time_reports:time-report-detail', kwargs={'pk': self.pk})
    def get_update_url(self): return reverse("time_reports:time-report-update", kwargs={"pk": self.pk})

    def get_days_in_month(self):
        return calendar.monthrange(self.start_date.year, self.start_date.month)[1]+1
    
    def days_range(self):
        return range(1, self.get_days_in_month())

    def get_weekend_days(self):
        weekends = []
        for day in calendar.Calendar().itermonthdates(self.start_date.year, self.start_date.month):
            if day.month != self.start_date.month:
                continue
            if day.weekday() == 5 or day.weekday() == 6: 
                weekends.append(day.day)
        return weekends

    def submit(self) -> None:
        self.status = SUBMITTED
        self.save()
        for projecrecord in self.projectrecord_set.filter(models.Q(status=DRAFT) | models.Q(status=REJECTED)):
            projecrecord.status = SUBMITTED
            if projecrecord.total_hours == 0:
                projecrecord.status = APPROVED
            projecrecord.save()

    def aggregate_project_lines(self) -> None:
        self.total_hours = 0
        self.total_amount_net = Money(0, 'PLN')
        self.total_amount_gross = Money(0, 'PLN')
        for projectrecord in self.projectrecord_set.all():
            self.total_hours += projectrecord.total_hours
            self.total_amount_net += projectrecord.total_amount_net
            self.total_amount_gross += projectrecord.total_amount_gross
        self.save()

    def update_status(self) -> None:
        statuses = []
        for project in self.projectrecord_set.all():
            statuses.append(project.status)

        for status in [REJECTED, DRAFT, SUBMITTED, APPROVED]:
            if status in statuses:
                if self.status != status:
                    self.status = status
                    self.save()
                return


    def validate_hours(self, request) -> bool:
        # sum hours from all projectime recrds and check is any day is over 24h
        valid_hours = True
        invalid_dates = []
        
        all_project_records = self.projectrecord_set.all()
        for day in self.days_range():
            date = datetime.date(self.start_date.year, self.start_date.month, day)
            total_hours = ProjectTime.objects.filter(Q(project_record__in = all_project_records) & Q(date=date)).aggregate(Sum('hours'))['hours__sum'] or 0
            if total_hours > 24:
                valid_hours = False
                invalid_dates.append(date)
        if not valid_hours:
            messages.error(request, format_html("Too many hours reported for: <strong>{}</strong>.", ", ".join(str(x) for x in invalid_dates)))
        return valid_hours       

    @classmethod
    def get_create_url(cls): return reverse('time_reports:time-report-create')

    @classmethod
    def get_list_url(cls): return reverse('time_reports:time-report-list')

class ProjectRecord(models.Model):
    time_report = models.ForeignKey('TimeReport', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=DRAFT)
    comment = models.TextField(blank=True, null=True)
    total_hours = models.PositiveSmallIntegerField(default=0)
    total_amount_net = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN', default=0)
    total_amount_gross = MoneyField(max_digits=10, decimal_places=2, default_currency='PLN', default=0)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.days = self.time_report.get_days_in_month()

    def __str__(self):
        return str(self.time_report) + ' - ' + self.project.name
    
    def get_full_record(self) -> dict:
        full_record_dict = {}
        full_record_dict['project_record'] = self
        full_record_dict['project'] = self.project
        days = self.time_report.get_days_in_month()
        for i in range(1, days):
            full_record_dict['day_'+str(i)] = None
        times = ProjectTime.objects.filter(project_record=self)
        for time in times:
            full_record_dict['day_'+str(time.date.day)] = time.hours
        full_record_dict['comment'] = self.comment
        return full_record_dict
    

    def get_hours_per_days(self) -> dict:
        project_time_data = self.projecttime_set.all().values('date', 'hours')
        return {entry['date'].day: entry['hours'] for entry in project_time_data}

    def set_hours_worked(self, hours_per_day: Dict[int, int], rates: Dict[int, MoneyField]) -> None:
        total_amount= Money(0, 'PLN') # TODO Fix hardcoded currency
        total_hours = 0

        self.projecttime_set.all().delete()
        for day, hours in hours_per_day.items():
            if hours is None or hours == 0:
                continue
            date = datetime.date(self.time_report.start_date.year, self.time_report.start_date.month, day)
            ProjectTime.objects.update_or_create(
                    project_record = self,
                    date=date,
                    defaults = {"hours": hours, "rate": rates[day]}
                ) 
            try:
                total_amount += hours * rates[day]
            except TypeError:
                # TODO: is this necesary?
                print(TypeError)
                pass
            total_hours += hours
            
        # self.total_hours = sum(value for value in hours_per_day.values() if value is not None)
        self.total_hours = total_hours
        self.total_amount_net = total_amount
        # TODO Fix hardcoded tax -> add it as a employee field
        self.total_amount_gross = total_amount * 1.23
        self.save()
        
    
    def set_as_submitted(self) -> None:
        self.status = SUBMITTED
        self.save()

    def get_approval_url(self) -> str:
        return reverse('approvals:approval-approve', kwargs={'type': 'project-time', 'pk': self.pk})    

    def get_rejection_url(self) -> str:
        return reverse('approvals:approval-reject', kwargs={'type': 'project-time', 'pk': self.pk})     

    def get_detail_url(self) -> str:
        return reverse('approvals:approval-detail', kwargs={'type': 'project-time', 'pk': self.pk})    

class ProjectTime(models.Model):
    project_record = models.ForeignKey('ProjectRecord', on_delete=models.CASCADE)
    date = models.DateField()
    hours = models.PositiveSmallIntegerField(validators=[MaxValueValidator(24)])
    rate = MoneyField(max_digits=6, decimal_places=2, default_currency='PLN', default=0)

    def __str__(self):
        return str(self.project_record) + ' - ' + self.date.strftime('%Y.%m.%d')
    
