from typing import Any
from django import http
from django.forms import formset_factory
from django.http.response import HttpResponse
from django.urls import reverse
from .models import TimeReport, ProjectRecord
from django.views import generic, View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
# from .forms import TimeReportCreateForm, ProjectRecordForm, ProjectRecordFormSet, ProjectLineForm, ProjectLineFormset
from .forms import TimeReportCreateForm, TimeEntryForm
from django.contrib import messages
from django.utils.html import format_html
from django.shortcuts import  get_object_or_404, redirect, render
from datetime import datetime
# from django.shortcuts import render

class TimeReportList(PermissionRequiredMixin, SuccessMessageMixin, generic.FormView, generic.ListView):
    template_name = 'time_reports/time_report_list.html'
    context_object_name = 'time_reports'
    permission_required = 'time_reports.view_time_report'
    form_class = TimeReportCreateForm

    def get_form(self):
        return self.form_class(employee = self.employee)

    def get(self, request, *args, **kwargs):
        self.employee = self.request.user.employee
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return self.employee.timereport_set.order_by('-start_date')

class TimeReportCreate(PermissionRequiredMixin, SuccessMessageMixin, View):
    # template_name = 'time_reports/time_report_list.html'
    # context_object_name = 'time_reports'
    # form_class = TimeReportCreateForm
    permission_required = 'time_reports.add_time_report'
    http_method_names = ['post']

    # allowed methods

    def post(self, request, *args, **kwargs):
        self.employee = self.request.user.employee
        time_report_date = datetime.date(datetime.strptime(request.POST.get("timereportselect"), "%Y-%m-%d"))
        # strptime(request.POST.get("timereportselect"), "%Y-%m-%d") 
        if time_report_date in self.employee.get_empty_time_report():
            new_time_report = TimeReport.objects.create(employee=self.employee, start_date=time_report_date)
            new_time_report.save()
            messages.success(request, format_html("Time report <strong>{}</strong> created.", time_report_date.strftime('%B %Y')))
            return redirect(new_time_report.get_absolute_url())
        messages.error(request, format_html("Time report not created.", time_report_date.strftime('%B %Y')))
        return TimeReport.get_list_url()
        # return super().post(request, *args, **kwargs)

class TimeReportDetail(PermissionRequiredMixin, generic.DetailView):
    model = TimeReport
    template_name = 'time_reports/time_report_detail.html'
    context_object_name = 'time_report'
    permission_required = 'time_reports.view_time_report'

class TimeReportUpdate(PermissionRequiredMixin, SuccessMessageMixin, View):
    template_name = 'time_reports/time_report_update_form.html'
    permission_required = 'time_reports.add_time_report'
    TimeEntryFormset = formset_factory(TimeEntryForm, can_delete=True, extra=0, min_num=1)   
    time_report = None        
    formset = None
    days_in_time_report = None

    def setup(self, request, *args, **kwargs):
        self.time_report = TimeReport.objects.get(pk=kwargs['pk'])
        initial = []
        project_records = ProjectRecord.objects.filter(time_report=self.time_report)
        for project in project_records:
            initial.append(project.get_full_record())
        self.formset = self.TimeEntryFormset(request.POST or None, initial=initial, form_kwargs={'time_report': self.time_report}, prefix="ProjectLines")
        self.days_in_time_report = self.time_report.get_days_in_month()
        self.context = {
            'formset': self.formset, 
            'time_report': self.time_report, 
            'days': range(1, self.days_in_time_report),
            'total_columns': self.days_in_time_report + 2,
            }
        return super().setup(request, *args, **kwargs)
    
    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self.time_report.status in ['submitted', 'approved']:
            messages.error(request, format_html("Time report <strong>{}</strong> is already submitted or approved.", self.time_report))
            return redirect(self.time_report.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, 'time_reports/time_report_update_form.html', context=self.context)
    
    def post(self, request, *args, **kwargs):
        # print("test")
        # for form in self.formset:
        #     form.full_clean()
        #     print(form.errors)
        #     print(form.is_valid())
        #     print(form.cleaned_data)

        if not self.formset.is_valid():
            messages.error(request, format_html("Time report <strong>{}</strong> not updated.",  self.time_report))
            return render(request, 'time_reports/time_report_update_form.html', context=self.context)
        for form in self.formset:
            if form.has_changed():
                form.save()
        self.time_report.aggregate_project_lines()
        if not self.time_report.validate_hours(request):
            return render(request, 'time_reports/time_report_update_form.html', context=self.context)
        if self.formset.data["mode"] == "submit":
            self.time_report.submit() 
        messages.success(request, format_html("Time report <strong>{}</strong> updated.",  self.time_report))
        return redirect(self.time_report.get_absolute_url())

class ApprovalsList(PermissionRequiredMixin, SuccessMessageMixin, generic.ListView):
    template_name = 'time_reports/approvals_list.html'
    context_object_name = 'approvals'
    permission_required = 'time_reports.view_time_report' # TODO: change permisssion to appropriate one

    def get_queryset(self):
        current_user = self.request.user.employee
        context = {}
        context['time_reports'] = ProjectRecord.objects.filter(
            status='submitted', #TODO: fix hardcoding
            project__managers=current_user #TODO: fix relation name
        ).order_by('project__name').order_by('time_report__employee__name').order_by('time_report__start_date')
        # print (submitted_ProjectRecord)
        return context
    
class ApprovalDecision(PermissionRequiredMixin, SuccessMessageMixin, View):
    approval_item = None
    approval_item_type = None
    approval_list_url = None

    def has_permission(self) -> bool:
        if self.request.user.employee in self.approval_item.project.managers.all():
            return True
        return False

    def setup(self, request, *args, **kwargs):
        self.approval_list_url = reverse('time_reports:approval-list')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any):    
        if kwargs['type'] not in ['project']:
            messages.error(request, format_html("Type <strong>{}</strong> not supported.", kwargs['type']))
            return redirect(self.approval_list_url)
        if kwargs['type'] == 'project':
            self.approval_item = get_object_or_404(ProjectRecord, id=kwargs['pk'])
            self.approval_item_type = 'Project'
        if self.approval_item.status != 'submitted':
            messages.error(request, format_html("{} is not submitted.", self.approval_item_type))
            return redirect(self.approval_list_url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        if kwargs['decision'] == 'approve':
            messages.success(request, format_html("{} approved.", self.approval_item_type))
            self.approval_item.status = 'approved'
        if kwargs['decision'] == 'reject':
            messages.error(request, format_html("{} rejected.", self.approval_item_type))
            self.approval_item.status = 'rejected'
        self.approval_item.save()
        self.approval_item.time_report.update_status()
        return redirect(self.approval_list_url)

