from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin

from dal import autocomplete
from .models import Client
from django.db import models

# class ClientList(generic.ListView):
class ClientList(PermissionRequiredMixin, generic.ListView):
    permission_required = 'users.view_user'
    template_name = 'clients/client_list.html'
    def get_queryset(self):
        return None

class ClientDetail(generic.DetailView):
    pass

class ClientCreate( generic.CreateView):
    pass

class ClientUpdate( generic.UpdateView):
    pass    

class ClientDelete( generic.DeleteView):
    pass

class EmClientAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Client.objects.all().order_by('name')
        if self.q:
            qs = qs.filter(models.Q(name__icontains=self.q))
        return qs