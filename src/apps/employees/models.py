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

class MonthsInDates:
    def __init__(self, start_date, end_date):
        self.start_date_month = start_date.replace(day=1)

        next_month = datetime.date.today().replace(day=28) + datetime.timedelta(days=4)
        first_day_next_month = next_month.replace(day=1)
        
        if end_date is None:
            self.end_date_month = first_day_next_month
            return None
        self.end_date_month = end_date.replace(day=1)
        return None

    def __iter__(self):
        self.current_date = self.start_date_month
        return self

    def next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1, day=1)
            return
        self.current_date = self.current_date.replace(month=self.current_date.month+1, day=1)

    def __next__(self):
        if self.current_date <= self.end_date_month:
            current_date = self.current_date
            self.next_month()
            return current_date
        raise StopIteration

class Employee(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nip = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='EmployeeAvatar/', blank=True)
    avatar_checksum = models.CharField(blank=True, max_length=50)

    @classmethod
    def get_list_url(cls):
        return reverse('employees:employee-list')

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name

    def email(self):
        return self.user.username

    def first_name(self):
        return self.user.first_name

    def last_name(self):
        return self.user.last_name

    def update_slug(self, string_to_slugify):
        if self.slug != string_to_slugify:
            self.slug = unique_slugify(self, string_to_slugify)
            self.save()

    def save(self, *args, **kwargs):
        if not self.slug:
            name_to_slugify = self.user.first_name + ' ' + self.user.last_name
            self.slug = unique_slugify(self, name_to_slugify)
        if self.avatar:
            this = Employee.objects.get(user=self.user)
            if this.avatar != self.avatar:
                this.avatar.delete(save=False)
        super(Employee, self).save(*args, **kwargs)
        if self.avatar:
            image = Image.open(self.avatar.path)
            image = image.resize((256, 256), Image.ANTIALIAS)
            image.save(self.avatar.path)

    def deactivate(self):
        self.user.is_active = False
        self.user.save()

    def activate(self):
        self.user.is_active = True
        self.user.save()

    def redirect_if_inactive(self, request, callback):
        if not self.user.is_active:
            messages.error(request, format_html("Employee <strong>{}</strong> is inactive.", self))
            return redirect(self.get_absolute_url())
        return callback

    def get_current_contract(self):
        today = datetime.date.today()
        return self.contract_set.filter(start_date__lte=today).filter(models.Q(end_date__gte=today) | models.Q(end_date=None) ).first()

    def get_current_rate(self):
        today = datetime.date.today()
        return  self.rate_set.filter(start_date__lte=today).filter(models.Q(end_date__gte=today) | models.Q(end_date=None) ).first()

    def get_rates_for_period(self, start_date, end_date):
        return self.rate_set.filter(start_date__lte=end_date).filter(models.Q(end_date__gte=start_date) | models.Q(end_date=None) ).all()

    def get_dict_of_rates_per_day(self, month_start_date: datetime.date, is_chargable: bool) -> dict():
        next_month = month_start_date.replace(day=28) + datetime.timedelta(days=4)
        month_end_date = next_month - datetime.timedelta(days=next_month.day)
        rates = self.get_rates_for_period(month_start_date, month_end_date)
        rates_per_day = {}
        for rate in rates:
            start = max(rate.start_date, month_start_date)
            end = month_end_date
            if rate.end_date is not None:
                end = min(rate.end_date, month_end_date)
            for i in range(start.day, end.day + 1):
                if is_chargable:
                    rates_per_day[i] = rate.chargable
                    continue
                rates_per_day[i] = rate.internal
        return rates_per_day


    def get_empty_time_report(self):
        contract_month_set = set()
        tr_month_set = set()

        contracts = self.contract_set.all().order_by('start_date')
        time_reports = self.timereport_set.all().order_by('start_date')

        for contract in contracts:
            # print(contract.employee , contract, contract.start_date, contract.end_date)
            for date_in_contract in MonthsInDates(contract.start_date, contract.end_date):
                # print (date_in_contract)
                contract_month_set.add(date_in_contract)
        for time_report in time_reports:
            for date_in_time_report in MonthsInDates(time_report.start_date, time_report.start_date):
                tr_month_set.add(date_in_time_report)
        month_set = contract_month_set - tr_month_set
        return sorted(list(month_set))
    
    def get_absolute_url(self): return reverse("employees:employee-detail", kwargs={"slug": self.slug})
    def get_update_url(self): return reverse("employees:employee-update", kwargs={"slug": self.slug})
    def get_deactivate_url(self): return reverse("employees:employee-deactivate", kwargs={"slug": self.slug})
    def get_activate_url(self): return reverse("employees:employee-activate", kwargs={"slug": self.slug})
    def get_contract_create_url(self): return reverse("employees:contract-create", kwargs={"slug": self.slug})
    def get_rate_create_url(self): return reverse("employees:rate-create", kwargs={"slug": self.slug})

class Contract(models.Model):
    PERMANENT = 'PER'
    B2B_CONTRACT = 'B2B'
    CONTRACT_TYPES = [(PERMANENT, 'Permanent'), (B2B_CONTRACT, 'B2B Contract')]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    name = models.CharField(blank=False, null=False, max_length=100)
    sign_date = models.DateField(blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=True, null=True)
    scan = models.FileField(upload_to='EmployeeContract/', blank=True)
    type = models.CharField(blank=False, null=False, choices=CONTRACT_TYPES, max_length=3, default=B2B_CONTRACT)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    def have_overlapping_dates(self):
        check_start = self.start_date
        check_end = self.end_date

        if check_end is None:
            overlaps = Contract.objects.filter(employee=self.employee).filter(
                models.Q(end_date=None) | models.Q(end_date__gte=check_start)
            ).exclude(id=self.id).exists()

        if check_end is not None:
            overlaps = Contract.objects.filter(employee=self.employee).filter(
                (models.Q(end_date=None) & models.Q(start_date__lte=check_end)) | 
                (models.Q(start_date__lte=check_start) & models.Q(end_date__gte=check_start)) |
                (models.Q(start_date__lte=check_end) & models.Q(end_date__gte=check_end)) |
                (models.Q(start_date__gte=check_start) & models.Q(end_date__lte=check_end)) |
                (models.Q(start_date__lte=check_start) & models.Q(end_date__gte=check_end)) 
            ).exclude(id=self.id).exists()
        return overlaps

    def get_absolute_url(self): return reverse("employees:contract-detail", kwargs={"pk": self.pk, "employee": self.employee.slug})
    def get_update_url(self): return reverse("employees:contract-update", kwargs={"pk": self.pk, "employee": self.employee.slug})
    def get_delete_url(self): return reverse("employees:contract-delete", kwargs={"pk": self.pk, "employee": self.employee.slug})

class Rate(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    chargable =  MoneyField(max_digits=14, decimal_places=2, default_currency='PLN', blank=False, null=False)
    internal = MoneyField(max_digits=14, decimal_places=2, default_currency='PLN', blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        # return f"{self.employee.__str__()} - {self.start_date.__str__()}"
        if self.end_date is not None:
            return self.start_date.strftime("%d.%m.%Y") + " - " + self.end_date.strftime("%d.%m.%Y")
        return self.start_date.strftime("%d.%m.%Y")

    def have_overlapping_dates(self):
        check_start = self.start_date
        check_end = self.end_date
        
        if check_end is None:
            overlaps = Rate.objects.filter(employee=self.employee).filter(
                models.Q(end_date=None) | models.Q(end_date__gte=check_start)
            ).exclude(id=self.id).exists()
        if check_end is not None:
            overlaps = Rate.objects.filter(employee=self.employee).filter(
                models.Q(start_date__lte=check_end) & models.Q(end_date=None) | (
                    (models.Q(start_date__lte=check_start) & models.Q(end_date__gte=check_start)) |
                    (models.Q(start_date__lte=check_end) & models.Q(end_date__gte=check_end)) 
                ) 
            ).exclude(id=self.id).exists()
        return overlaps

    def get_absolute_url(self): return reverse("employees:rate-detail", kwargs={"pk": self.pk, "employee": self.employee.slug})
    def get_update_url(self): return reverse("employees:rate-update", kwargs={"pk": self.pk, "employee": self.employee.slug})
    def get_delete_url(self): return reverse("employees:rate-delete", kwargs={"pk": self.pk, "employee": self.employee.slug})