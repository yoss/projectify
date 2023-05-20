from typing import Dict
from django import forms
from .models import DRAFT, REJECTED, TimeReport, ProjectRecord, ProjectTime
from ..projects.models import Project
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, HTML, MultiWidgetField, Div, Button, Row, Column
from crispy_forms.bootstrap import FormActions
from django.utils.html import format_html
from django.forms import modelformset_factory, inlineformset_factory, formset_factory
from dal import autocomplete

class TimeReportCreateForm(forms.Form):
    timereportselect = forms.ChoiceField(label="Select Time Report",required=False)

    def get_choices(self):
        choices = []
        for tr in self.employee.get_empty_time_report():
            choices.append((tr, tr.strftime('%B %Y')))
        return choices

    def __init__(self, employee, *args, **kwargs):
        self.employee = employee
        super().__init__(*args, **kwargs)
        self.fields['timereportselect'].choices = map(lambda x: (x, x.strftime('%B %Y')), self.employee.get_empty_time_report())
        self.action = TimeReport.get_create_url()


    @property
    def helper(self):
        helper = FormHelper()
        helper.form_class = 'form-horizontal'
        helper.label_class = 'col-lg-4'
        helper.field_class = 'col-lg-8'
        helper.form_action = self.action
        helper.layout = Layout(

            Div(
                HTML('<h5 class="modal-title" id="modal-title">Create new Time report</h5>'),
                Button('close', ' ', css_class='btn-close', data_bs_dismiss='modal', aria_label='Close'),
                css_class='modal-header'
            ),
            Div(
                'timereportselect',
                css_class='modal-body',
                css_id='modal-body',
            ),
            Div(
                Button('cancel', 'Cancel', css_class='btn btn-secondary', data_bs_dismiss='modal'),
                Submit('submit', 'Add Time report', css_class='btn btn-success'),
                css_class='modal-footer'
            )
        )
        return helper

class TimeEntryForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Project.objects.all(), 
        widget=autocomplete.ModelSelect2(url='projects:project-autocomplete', attrs={'class': 'p0 custom-select-sm'}), 
        label=""
        )
    
    time_report = ""
    project_record = forms.ModelChoiceField(queryset=ProjectRecord.objects.all(), widget=forms.HiddenInput(), label="", required=False)

    def __init__(self, time_report, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.time_report = time_report
        num_days = time_report.get_days_in_month()
        weekends = time_report.get_weekend_days()

        # Generate a form field for each day in the month
        for i in range(1, num_days):
            field_name = f"day_{i}"
            self.fields[field_name] = forms.IntegerField(
                label = "",
                min_value = 0,
                max_value = 24,
                required = False,
                # error_css_class = 'is-invalid no-image',
                widget = forms.TextInput(attrs={'class': 'p0 form-control-sm text-center', 'placeholder': '-',  'style': 'padding: 2px; width: 4ch'}),
            )
            if i in weekends:
                self.fields[field_name].widget.attrs['style'] += '; background-color: #ddd' 
        self.fields['comment'] = forms.CharField(required=False, label = "", widget=forms.TextInput(attrs={'class': 'p0 p0 form-control-sm'}))


        if kwargs.get("initial") is not None and kwargs["initial"]["project_record"].status not in [DRAFT, REJECTED]:
            for key in self.fields.keys():
                self.fields[key].disabled = True
                self.fields[key].required = False
                    # field.widget.attrs['disabled'] = 'disabled'
                    # field.widget.attrs['required'] = False


    # def clean_project_record(self):
    #     project_record = self.cleaned_data.get('project_record')
    #     if project_record is None and 'DELETE'  not in self.changed_data:
    #         raise forms.ValidationError("Project record not set, contact administrator")
    #     return project_record
    
    def clean_project(self):
        
        project = self.cleaned_data.get('project')
        if project is None and 'DELETE' not in self.changed_data:
            raise forms.ValidationError("Project needs to be set before saving")
        
        if not project.is_active:
            raise forms.ValidationError(f"{project.name} is not active")
        if not project.is_public and self.time_report.employee not in project.members.all():
            raise forms.ValidationError(f"{project.name} is not public and you are not a member")
        return project
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     project = cleaned_data.get('project')
    #     project_record = cleaned_data.get('project_record')
    #     if project is None and project_record is None:
    #         raise forms.ValidationError("Project needs to be set before saving")
    #     return cleaned_data

    def clean(self):
        cleaned_data = super().clean()

        if self.cleaned_data.get('project') is None:
            return cleaned_data
        
        project = self.cleaned_data.get('project')
        self.rate_dictionary = self.time_report.employee.get_dict_of_rates_per_day(self.time_report.start_date, project.is_chargable)

        currencies = set()
        self.hours_dictionary = {}
        for day in range(1, self.time_report.get_days_in_month()):
            field_name = f"day_{day}"
            if self.cleaned_data.get(field_name) is None:
                continue
            self.hours_dictionary[day] = self.cleaned_data.get(field_name)
            if self.rate_dictionary.get(day) is None:
                raise forms.ValidationError("Missing rate for day, contact administration")
            currencies.add(self.rate_dictionary[day].currency)
        if len(currencies) > 1:
            raise forms.ValidationError("Different curriencies are not allowed in the same project line, contact administration") 

    #     
    # 
    # self.project = self.clean_project()
    #     self.rate_dictionary = self.time_report.employee.get_dict_of_rates_per_day(self.time_report.start_date, self.project.is_chargable)
    #     currencies = set()
    #     self.hours_dictionary = {}

    #     for day in range(1, self.time_report.get_days_in_month()):
    #         field_name = f"day_{day}"
    #         if self.cleaned_data.get(field_name) is None:
    #             continue
    #         self.hours_dictionary[day] = self.cleaned_data.get(field_name)

    #         if self.rate_dictionary.get(day) is None:
    #             raise forms.ValidationError("Missing rate for day, contact administration")
    #         currencies.add(self.rate_dictionary[day].currency)
    #     if len(currencies) > 1:
    #         raise forms.ValidationError("Different curriencies are not allowed in the same project line, contact administration") 
        return cleaned_data
        



    def save(self):
        project = self.cleaned_data.get('project')
        project_record = self.cleaned_data.get('project_record')

        if 'DELETE' in self.changed_data:
            if project_record is None:
                return
            project_record.delete()
            return

        if project_record is None and project is not None:
            project_record = ProjectRecord.objects.create(
                time_report=self.time_report,
                project=project,
                comment=self.cleaned_data.get('comment')
            )

        
        if 'project' in self.changed_data or 'comment' in self.changed_data:
            project_record.comment = self.cleaned_data.get('comment')
            project_record.project = project
            project_record.save()
# CREATE or UPDATE all ProjectTime objects for the month and set the hours worked for each day 
# OR remove all ProjectTime objects and create new ones only for the days that have been filled in ?

# which is better?

        # num_days = project_record.days
        # time_report_start_date = self.time_report.start_date
        # time_report_end_date = datetime.date(self.time_report.start_date.year, self.time_report.start_date.month, (num_days - 1))
        # rates = self.time_report.employee.get_rates_for_period(time_report_start_date, time_report_end_date)

        # rate_dictionary = self.time_report.employee.get_dict_of_rates_per_day(self.time_report.start_date, project.is_chargable)
        # hours_dictionary = {}
        # for i in range(1, project_record.days):
        #     field_name = f"day_{i}"
        #     hours_worked = self.cleaned_data.get(field_name)
        #     # if hours_worked is None:
        #     #     hours_worked = 0
        #     hours_dictionary[i] = hours_worked

        project_record.set_hours_worked(self.hours_dictionary, self.rate_dictionary)
        
        # for rate in rates:
            # start = max(rate.start_date, time_report_start_date)
            # end = time_report_end_date
            # if rate.end_date is not None:
            #     end = min(rate.end_date, time_report_end_date)

            # for i in range(start.day, end.day + 1):
            #     if project.is_chargable:
            #         fee[i] = rate.chargable
            #         continue
            #     fee[i] = rate.internal
        # print (rates)
        # print (fee)
        # for i in range(1, num_days):
        #     field_name = f"day_{i}"
        #     hours_worked = self.cleaned_data.get(field_name)
        #     if hours_worked is None:
        #         hours_worked = 0
        #     date = datetime.date(self.time_report.start_date.year, self.time_report.start_date.month, i)
        #     ProjectTime.objects.update_or_create(
        #             project_record = project_record,
        #             date=date,
        #             defaults = {"hours": hours_worked, "rate": fee[i]}
        #         )   

# TimeEntryFormset = formset_factory(TimeEntryForm, can_delete=True, extra=0, min_num=1)   

