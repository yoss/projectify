from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.html import format_html
from django.views import generic

from .forms import ContractForm, EmployeeCreateForm, EmployeeUpdateForm, RateForm
from .models import Contract, Employee, Rate


class EmployeeCreate(PermissionRequiredMixin, SuccessMessageMixin, generic.FormView):
    permission_required = 'employee.add_employee'
    form_class = EmployeeCreateForm
    template_name = 'employees/employee_create_form.html'
    employee = Employee()

    def form_valid(self, form):
        user = User.objects.create_user(
            username=form.cleaned_data['email'],
            email=form.cleaned_data['email'],
            first_name=form.cleaned_data['first_name'],
            last_name=form.cleaned_data['last_name'])
        self.employee.user = user
        self.employee.nip = form.cleaned_data['nip']
        self.employee.save()
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return format_html("Employee <strong>{}</strong> has been created", self.employee)

    def get_success_url(self):
        return self.employee.get_absolute_url()


class EmployeeList(PermissionRequiredMixin, generic.ListView):
    permission_required = 'employee.view_employee'
    model = Employee
    context_object_name = 'employees'
    def get_queryset(self):
        if self.kwargs['all']:
            return self.model.objects.all()
        return self.model.objects.filter(user__is_active=True)


class EmployeeDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'employee.view_employee'
    model = Employee
    context_object_name = 'employee'


class EmployeeUpdate(PermissionRequiredMixin, SuccessMessageMixin, generic.FormView):
    permission_required = 'employee.change_employee'
    form_class = EmployeeUpdateForm
    template_name = 'employees/employee_update_form.html'
    employee = Employee()

    def setup(self, request, *args, **kwargs):
        self.employee = get_object_or_404(Employee, slug=kwargs['slug'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.employee.redirect_if_inactive(request, callback=super().dispatch(request, *args, **kwargs))

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["employee"] = self.employee
        return context
    
    def get_initial(self, **kwargs):
        return {'email': self.employee.user.email, 'slug': self.employee.slug, 'nip': self.employee.nip, 'employee': self.employee}

    def form_valid(self, form):
        self.employee.user.email = form.cleaned_data['email']
        self.employee.user.username = form.cleaned_data['email']
        self.employee.nip = form.cleaned_data['nip']
        self.employee.user.save()
        self.employee.save()
        if form.cleaned_data['slug']:
            self.employee.update_slug(form.cleaned_data['slug'])
        return super().form_valid(form)

    def get_success_message(self, cleaned_data):
        return format_html("Employee <strong>{}</strong> has been updated", self.employee)
        # return "Employee <strong>" + html.escape(self.employee) + "</strong> has been updated"

    def get_success_url(self):
        return self.employee.get_absolute_url()

class EmployeeDeactivate(PermissionRequiredMixin, generic.View):
    permission_required = 'employee.delete_employee'
    model = Employee
    context_object_name = 'employee'
    http_method_names = ['post', 'get']

    def http_method_not_allowed(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['slug'])
        return redirect(employee.get_absolute_url())

    def get(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['slug'])
        popup_setup = {
            'modal_title': format_html("Deactivate {}" , employee),
            'modal_body': format_html("Are you sure you want to deactivate <strong>{}</strong>?" , employee),
            'modal_form_action': employee.get_deactivate_url(),
            'modal_submit': 'Deactivate',
            'modal_submit_class': 'btn btn-danger'
        }
        return JsonResponse(popup_setup)

    def post(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['slug'])
        employee.deactivate()
        messages.error(request, format_html("Employee <strong>{}</strong> has been deactivated", employee))
        # messages.error(request, "Employee <strong>" + html.escape(employee) + "</strong> has been deactivated")
        return redirect(Employee.get_list_url())
        
class EmployeeActivate(PermissionRequiredMixin, generic.View):
    permission_required = 'employee.add_employee'
    model = Employee
    context_object_name = 'employee'
    http_method_names = ['post', 'get']

    def http_method_not_allowed(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['slug'])
        return redirect(employee.get_absolute_url())

    def get(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['slug'])
        popup_setup = {
            'modal_title': format_html("Activate {}" , employee),
            'modal_body': format_html("Are you sure you want to activate <strong>{}</strong>?" , employee),
            'modal_form_action': employee.get_activate_url(),
            'modal_submit': 'Activate',
            'modal_submit_class': 'btn btn-success'
        }
        return JsonResponse(popup_setup)

    def post(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['slug'])
        employee.activate()
        messages.success(request, format_html("Employee <strong>{}</strong> has been activated", employee))
        # messages.success(request, "Employee <strong>" + html.escape(employee) + "</strong> has been activated")
        return redirect(employee.get_absolute_url())

class ContractCreate(PermissionRequiredMixin, SuccessMessageMixin, generic.CreateView):
    permission_required = 'employee.add_contract'
    form_class = ContractForm
    model = Contract
    template_name = 'employees/contract_create_form.html'
    employee = Employee()

    def setup(self, request, *args, **kwargs):
        self.employee = get_object_or_404(Employee, slug=kwargs['slug'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.employee.redirect_if_inactive(request, callback=super().dispatch(request, *args, **kwargs))

    def get_initial(self):
        initial = super().get_initial()
        initial['employee'] = self.employee
        return initial

    def get_success_message(self, cleaned_data):
        return format_html("Contract for <strong>{}</strong> has been created", self.employee)
        # return format_html("Contract for <strong>{}</strong> has been created", html.escape(self.employee))
        # return f"Contract for {self.employee} has been created"

    def get_success_url(self):
        return self.employee.get_absolute_url()

    def form_valid(self, form):
        form.save()
        if form.instance.have_overlapping_dates():
            messages.warning(self.request, f"This contract has overlapping dates with other contract")
        return super().form_valid(form)

class ContractDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'employee.view_contract'
    model = Contract
    context_object_name = 'contract'

class ContractUpdate(PermissionRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    permission_required = 'employee.change_contract'
    form_class = ContractForm
    model = Contract
    template_name = 'employees/contract_update_form.html'
    context_object_name = 'contract'
    
    def dispatch(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['employee'])
        return employee.redirect_if_inactive(request, callback=super().dispatch(request, *args, **kwargs))

    def get_success_message(self, cleaned_data):
        return format_html("Contract for <strong>{}</strong> has been updated", self.object.employee)
        # return f"Contract for {self.object.employee} has been updated"

    def get_success_url(self):
        return self.object.employee.get_absolute_url()

    def form_valid(self, form):
        form.save()
        if form.instance.have_overlapping_dates():
            messages.warning(self.request, f"This contract has overlapping dates with other contract")
        return super().form_valid(form)

class ContractDelete(PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'employee.delete_contract'
    model = Contract
    context_object_name = 'contract'
    http_method_names = ['post', 'get']

    def dispatch(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['employee'])
        return employee.redirect_if_inactive(request, callback=super().dispatch(request, *args, **kwargs))

    def http_method_not_allowed(self, request, *args, **kwargs):
        contract = get_object_or_404(Contract, pk=kwargs['pk'])
        return redirect(contract.get_absolute_url())

    def get(self, request, *args, **kwargs):
        contract = get_object_or_404(Contract, pk=kwargs['pk'])
        popup_setup = {
            'modal_title': format_html('Delete contract {} ', contract),
            'modal_body': format_html('Are you sure you want to contract <strong>{}</strong> for {}?', contract, contract.employee),
            'modal_form_action': contract.get_delete_url(),
            'modal_submit': 'Delete',
            'modal_submit_class': 'btn btn-danger'
        }
        return JsonResponse(popup_setup)

    def post(self, request, *args, **kwargs):
        contract = get_object_or_404(Contract, pk=kwargs['pk'])
        contract.delete()
        messages.error(request, format_html("Contract <strong>{}</strong> for {} has been deleted", contract, contract.employee))
        # messages.error(request, f"Contract <strong>{contract}</strong> for {contract.employee} has been deleted")
        return redirect(contract.employee.get_absolute_url())

class RateCreate(PermissionRequiredMixin, SuccessMessageMixin, generic.CreateView):
    permission_required = 'employee.add_rate'
    form_class = RateForm
    model = Rate
    template_name = 'employees/rate_create_form.html'
    employee = Employee()

    def setup(self, request, *args, **kwargs):
        self.employee = get_object_or_404(Employee, slug=kwargs['slug'])
        return super().setup(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        return self.employee.redirect_if_inactive(request, callback=super().dispatch(request, *args, **kwargs))

    def get_initial(self):
        initial = super().get_initial()
        initial['employee'] = self.employee
        return initial

    def get_success_message(self, cleaned_data):
        return format_html("Rate for <strong>{}</strong> has been created", self.employee)
        # return f"Rate for {self.employee} has been created"

    def get_success_url(self):
        return self.employee.get_absolute_url()

class RateDetail(PermissionRequiredMixin, generic.DetailView):
    permission_required = 'employee.view_rate'
    model = Rate
    context_object_name = 'rate'

class RateUpdate(PermissionRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    permission_required = 'employee.change_rate'
    form_class = RateForm
    model = Rate
    template_name = 'employees/rate_update_form.html'
    context_object_name = 'rate'
    
    def dispatch(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['employee'])
        return employee.redirect_if_inactive(request, callback=super().dispatch(request, *args, **kwargs))

    def get_success_message(self, cleaned_data):
        return format_html("Rate for <strong>{}</strong> has been updated", self.object.employee)
        # return f"Rate for {self.object.employee} has been updated"

    def get_success_url(self):
        return self.object.employee.get_absolute_url()

class RateDelete(PermissionRequiredMixin, generic.DeleteView):
    permission_required = 'employee.delete_rate'
    model = Rate
    context_object_name = 'rate'
    http_method_names = ['post', 'get']

    def dispatch(self, request, *args, **kwargs):
        employee = get_object_or_404(Employee, slug=kwargs['employee'])
        return employee.redirect_if_inactive(request, callback=super().dispatch(request, *args, **kwargs))

    def http_method_not_allowed(self, request, *args, **kwargs):
        rate = get_object_or_404(Rate, pk=kwargs['pk'])
        return redirect(rate.get_absolute_url())

    def get(self, request, *args, **kwargs):
        rate = get_object_or_404(Rate, pk=kwargs['pk'])
        popup_setup = {
            'modal_title': format_html('Delete rate {} ', rate),
            'modal_body': format_html('Are you sure you want to rate for for {}?', rate.employee),
            'modal_form_action': rate.get_delete_url(),
            'modal_submit': 'Delete',
            'modal_submit_class': 'btn btn-danger'
        }
        return JsonResponse(popup_setup)

    def post(self, request, *args, **kwargs):
        rate = get_object_or_404(Rate, pk=kwargs['pk'])
        rate.delete()
        messages.error(request, format_html("Rate for <strong>{}</strong> has been deleted", rate.employee))
        messages.error(request, f"Rate for {rate.employee} has been deleted")
        return redirect(rate.employee.get_absolute_url())