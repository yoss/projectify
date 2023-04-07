from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.html import format_html
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from .models import Project
from .forms import ProjectForm
from django.db import models
from dal import autocomplete

class ProjectList(PermissionRequiredMixin, generic.ListView):
    permission_required = 'projects.view_project'
    model = Project
    context_object_name = 'projects'
    def get_queryset(self):
        if self.kwargs['all']:
            return self.model.objects.all()
        return self.model.objects.filter(is_active=True)
        
class ProjectDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'projects.view_project'
    model = Project
    context_object_name = 'project'
    
class ProjectCreate(PermissionRequiredMixin, SuccessMessageMixin, generic.CreateView):
    permission_required = 'projects.add_project'
    form_class = ProjectForm
    model = Project
    template_name = 'projects/project_create_form.html'

    def get_success_message(self, cleaned_data):
        return format_html("Project <strong>{}</strong> has been created", self.object)

    def get_success_url(self):
        return self.object.get_absolute_url()

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)


class ProjectUpdate(PermissionRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    permission_required = 'projects.change_project'
    form_class = ProjectForm
    model = Project
    template_name = 'projects/project_update_form.html'
    context_object_name = 'project'
    
    def get_success_message(self, cleaned_data):
        return format_html("Project <strong>{}</strong> has been updated", self.object)

    def get_success_url(self):
        return self.object.get_absolute_url()

class ProjectToggle(PermissionRequiredMixin, generic.View):
    permission_required = 'projects.delete_project'
    model = Project
    context_object_name = 'project'
    http_method_names = ['post', 'get']

    def setup(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, slug=kwargs['slug'])
        return super().setup(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        return redirect(self.project.get_absolute_url())

class ProjectDeactivate(ProjectToggle):
    def get(self, request, *args, **kwargs):
        popup_setup = {
            'modal_title': format_html('Deactivate project {} ', self.project),
            'modal_body': format_html('Are you sure you want to deactivate project <strong>{}</strong>?', self.project),
            'modal_form_action': self.project.get_deactivate_url(),
            'modal_submit': 'Deactivate',
            'modal_submit_class': 'btn btn-danger'
        }
        return JsonResponse(popup_setup)

    def post(self, request, *args, **kwargs):
        self.project.is_active = False
        self.project.save()
        messages.error(request, format_html("Project <strong>{}</strong> has been deactivated", self.project))
        return redirect(Project.get_list_url())


class ProjectActivate(ProjectToggle):
    def get(self, request, *args, **kwargs):
        popup_setup = {
            'modal_title': format_html('Activate project {} ', self.project),
            'modal_body': format_html('Are you sure you want to activate project <strong>{}</strong>?', self.project),
            'modal_form_action': self.project.get_activate_url(),
            'modal_submit': 'Activate',
            'modal_submit_class': 'btn btn-success'
        }
        return JsonResponse(popup_setup)

    def post(self, request, *args, **kwargs):
        self.project.is_active = True
        self.project.save()
        messages.success(request, format_html("Project <strong>{}</strong> has been activated", self.project))
        return redirect(self.project.get_absolute_url())

class ProjectAutocomplete(LoginRequiredMixin, autocomplete.Select2QuerySetView):
    def get_queryset(self):

        # Don't forget to filter out results depending on the visitor !

        # filter all active visible projects and hidden projects where user is member
        qs = Project.objects.all().filter(is_active=True).filter(models.Q(is_public=True) | models.Q(members__in=[self.request.user.employee])).order_by('name')  
        # qs = Project.objects.all().filter(user__is_active=True).order_by('user__last_name')
        if self.q:
            qs = qs.filter(models.Q(name__icontains=self.q))
        return qs