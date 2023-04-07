from django.urls import path
from . import views

app_name = 'projects'
urlpatterns = [
    path('', views.ProjectList.as_view(), name='project-list', kwargs={'all': False}),
    path('all/', views.ProjectList.as_view(), name='project-list-all', kwargs={'all': True}),
    path('new/', views.ProjectCreate.as_view(), name='project-create'),
    path('api/', views.ProjectAutocomplete.as_view(), name='project-autocomplete'),
    path('<slug:slug>/', views.ProjectDetail.as_view(), name='project-detail'),
    path('<slug:slug>/edit', views.ProjectUpdate.as_view(), name='project-update'),
    path('<slug:slug>/deactivate', views.ProjectDeactivate.as_view(), name='project-deactivate'),
    path('<slug:slug>/activate', views.ProjectActivate.as_view(), name='project-activate'),
]
