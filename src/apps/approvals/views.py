from typing import Any
from django import http
from django.urls import reverse
from ..time_reports.models import ProjectRecord
from django.views import generic, View
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.html import format_html
from django.shortcuts import  get_object_or_404, redirect, render

class ApprovalsList(PermissionRequiredMixin, SuccessMessageMixin, generic.ListView):
    template_name = 'approvals/approvals_list.html'
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
        self.approval_list_url = reverse('approvals:approval-list')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any):    
        if kwargs['type'] not in ['project-time']:
            messages.error(request, format_html("Type <strong>{}</strong> not supported.", kwargs['type']))
            return redirect(self.approval_list_url)
        if kwargs['type'] == 'project-time':
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



class ApprovalDetails(PermissionRequiredMixin, SuccessMessageMixin, View):
    # TODO: merge ApprovalDetails with ApprovalDecision
    template_name = 'approvals/approvals_detail.html'
    approval_item = None
    approval_item_type = None
    approval_list_url = None

    def has_permission(self) -> bool:
        if self.request.user.employee in self.approval_item.project.managers.all():
            return True
        return False

    def setup(self, request, *args, **kwargs):
        self.approval_list_url = reverse('approvals:approval-list')
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request: http.HttpRequest, *args: Any, **kwargs: Any):    
        if kwargs['type'] not in ['project-time']:
            messages.error(request, format_html("Type <strong>{}</strong> not supported.", kwargs['type']))
            return redirect(self.approval_list_url)
        if kwargs['type'] == 'project-time':
            self.approval_item = get_object_or_404(ProjectRecord, id=kwargs['pk'])
            self.approval_item_type = 'Project'
            # self.context_object_name = 'project_time'
        if self.approval_item.status != 'submitted':
            messages.error(request, format_html("{} is not submitted.", self.approval_item_type))
            return redirect(self.approval_list_url)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, context={'approval': self.approval_item, 'approval_item_type': self.approval_item_type})
