from django.db import models
from django import forms
from .models import Employee, Contract, Rate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, MultiWidgetField
from crispy_forms.bootstrap import FormActions
from django.utils.html import format_html
import datetime

class EmployeeCreateForm(forms.Form):
    email = forms.EmailField()
    first_name = forms.CharField()
    last_name = forms.CharField()
    nip = forms.CharField(max_length=20, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancel_url = Employee.get_list_url()

    def clean_email(self):
        email = self.cleaned_data['email']
        if Employee.objects.filter(user__username = email).exists():
            raise forms.ValidationError("Employee " + email + " already exists.")
        return email

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-lg-2'
        helper.field_class = 'col-lg-4'
        helper.layout = Layout(
            'email',
            'first_name',
            'last_name',
            'nip',
            FormActions(
                Submit('submit', 'Save', css_class='btn btn-primary btn-sm'),
                HTML(format_html('<a class="btn btn-outline-primary btn-sm" href="{}">Cancel</a>', self.cancel_url)),
            ),
        )
        return helper

class EmployeeUpdateForm(forms.Form):
    email = forms.EmailField()
    slug = forms.CharField(max_length=100, required=False, label='URL Slug')
    nip = forms.CharField(max_length=20, required=False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cancel_url = self.initial['employee'].get_absolute_url()

    def clean_email(self):
        email = self.cleaned_data['email']
        if email == self.initial['email']:
            return email
        if Employee.objects.filter(user__username = email).exists():
            raise forms.ValidationError("Employee " + email + " already exists.")
        return email

    @property
    def helper(self):
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-lg-2'
        helper.field_class = 'col-lg-4'
        helper.layout = Layout(
            'email',
            'slug',
            'nip',
            FormActions(
                Submit('submit', 'Save', css_class='btn btn-primary btn-sm'),
                HTML(format_html('<a class="btn btn-outline-primary btn-sm" href="{}">Cancel</a>', self.cancel_url)),
            ),
        )
        return helper

class ContractForm(forms.ModelForm):
    class Meta:
        model = Contract
        fields = ['employee', 'name', 'type', 'start_date', 'end_date', 'sign_date', 'scan', 'comment']
            
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].disabled = True
        self.fields['sign_date'].widget.input_type = 'date'
        self.fields['start_date'].widget.input_type = 'date'
        self.fields['end_date'].widget.input_type = 'date'
        if type(self.initial['employee']) == Employee:
            self.cancel_url = self.initial['employee'].get_absolute_url()
        if hasattr(self.instance, "employee"):
            self.cancel_url = self.instance.employee.get_absolute_url()

    def clean_employee(self):
        employee = self.cleaned_data['employee']
        if employee.user.is_active == False:
            raise forms.ValidationError(format_html("Employee {} is inactive.", employee))
        return employee

    def clean_sign_date(self):
        sign_date = self.cleaned_data['sign_date']
        if sign_date > datetime.date.today():
            raise forms.ValidationError("Sign date cannot be in the future.")
        return sign_date

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        sign_date = cleaned_data.get('sign_date')
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("Start date cannot be after end date.")
        # if sign_date and start_date and sign_date > start_date:
        #     raise forms.ValidationError("Sign date cannot be after start date.")

    @property
    def helper(self):    
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-lg-2'
        helper.field_class = 'col-lg-4'
        helper.layout = Layout(
            'employee',
            'name',
            'type',
            'sign_date',
            'start_date',
            'end_date',
            'scan',
            'comment',
            FormActions(
                Submit('submit', 'Save', css_class='btn btn-primary btn-sm'),
                HTML(format_html('<a class="btn btn-outline-primary btn-sm" href="{}">Cancel</a>', self.cancel_url)),
            ),
        )
        return helper

class RateForm(forms.ModelForm):
    class Meta:
        model = Rate
        fields = ['employee', 'chargable', 'internal', 'start_date', 'end_date', 'comment']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['employee'].disabled = True
        self.fields['start_date'].widget.input_type = 'date'
        self.fields['end_date'].widget.input_type = 'date'
        if type(self.initial['employee']) == Employee:
            self.cancel_url = self.initial['employee'].get_absolute_url()
        if hasattr(self.instance, "employee"):
            self.cancel_url = self.instance.employee.get_absolute_url()

    def clean_employee(self):
        employee = self.cleaned_data['employee']
        if employee.user.is_active == False:
            raise forms.ValidationError(format_html("Employee {} is inactive.", employee))
        return employee

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        employee = cleaned_data['employee']
        overlaps = False

        if start_date and end_date and start_date > end_date:
            self.add_error('start_date', "Start date cannot be after end date.")
            self.add_error('end_date', "Start date cannot be after end date.")
            # raise forms.ValidationError("Start date cannot be after end date.")
            
        if end_date is None:
            overlaps = Rate.objects.filter(employee=employee).filter(
                models.Q(end_date=None) | models.Q(end_date__gte=start_date)
            ).first()
            
        if end_date is not None:
            overlaps = Rate.objects.filter(employee=employee).filter(
                (models.Q(end_date=None) & models.Q(start_date__lte=end_date)) | 
                (models.Q(start_date__lte=start_date) & models.Q(end_date__gte=start_date)) |
                (models.Q(start_date__lte=end_date) & models.Q(end_date__gte=end_date)) |
                (models.Q(start_date__gte=start_date) & models.Q(end_date__lte=end_date)) |
                (models.Q(start_date__lte=start_date) & models.Q(end_date__gte=end_date)) 
            ).first()
        if overlaps and overlaps != self.instance:
            self.add_error('start_date', format_html("Overlapping dates with <a href='{}'>existing rate</a>.", overlaps.get_absolute_url()))
            self.add_error('end_date', format_html("Overlapping dates with <a href='{}'>existing rate</a>.", overlaps.get_absolute_url()))
            # self.add_error('end_date', mark_safe(f"Overlapping dates with <a href='{overlaps.get_absolute_url()}'>existing rate</a>."))
            # self.add_error('end_date', "Overlapping dates with other rate.")
            # raise forms.ValidationError("Start date cannot be after end date.")

            
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

    @property
    def helper(self):    
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-lg-2'
        helper.field_class = 'col-lg-4'
        helper.layout = Layout(
            'employee',
            MultiWidgetField(
                'chargable',
                attrs=(
                    {'style': 'width: 50%; display: inline-block'}
                )
            ),
            MultiWidgetField(
                'internal',
                attrs=(
                    {'style': 'width: 50%; display: inline-block'}
                )
            ),
            'start_date',
            'end_date',
            'comment',
            FormActions(
                Submit('submit', 'Save', css_class='btn btn-primary btn-sm'),
                HTML(format_html('<a class="btn btn-outline-primary btn-sm" href="{}">Cancel</a>', self.cancel_url)),
            ),
        )
        return helper