from django.views import generic
from django.contrib.auth.mixins import PermissionRequiredMixin

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
