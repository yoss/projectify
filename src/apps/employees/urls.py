from django.urls import path
from . import views

app_name = 'employees'
urlpatterns = [
    path('', views.EmployeeList.as_view(), name='employee-list', kwargs={'all': False}),
    path('all/', views.EmployeeList.as_view(), name='employee-list-all', kwargs={'all': True}),
    path('new/', views.EmployeeCreate.as_view(), name='employee-create'),
    path('api/', views.EmployeeAutocomplete.as_view(), name='employee-autocomplete'),
    path('<slug:slug>/', views.EmployeeDetail.as_view(), name='employee-detail'),
    path('<slug:slug>/edit', views.EmployeeUpdate.as_view(), name='employee-update'),
    path('<slug:slug>/deactivate', views.EmployeeDeactivate.as_view(), name='employee-deactivate'),
    path('<slug:slug>/activate', views.EmployeeActivate.as_view(), name='employee-activate'),
    path('<slug:slug>/contract/new', views.ContractCreate.as_view(), name='contract-create'),
    path('<slug:employee>/contract/<int:pk>', views.ContractDetail.as_view(), name='contract-detail'),
    path('<slug:employee>/contract/<int:pk>/edit', views.ContractUpdate.as_view(), name='contract-update'),
    path('<slug:employee>/contract/<int:pk>/delete', views.ContractDelete.as_view(), name='contract-delete'),
    path('<slug:slug>/rate/new', views.RateCreate.as_view(), name='rate-create'),
    path('<slug:employee>/rate/<int:pk>', views.RateDetail.as_view(), name='rate-detail'),
    path('<slug:employee>/rate/<int:pk>/edit', views.RateUpdate.as_view(), name='rate-update'),
    path('<slug:employee>/rate/<int:pk>/delete', views.RateDelete.as_view(), name='rate-delete'),


    # path('<slug:slug>/tr', views.contract_dates.as_view(), name='tr-dates'),

]
