from django.urls import path
from . import views

app_name = 'clients'
urlpatterns = [
    path('', views.ClientList.as_view(), name='list'),
    path('q/', views.EmClientAutocomplete.as_view(), name='client-autocomplete'),
]
