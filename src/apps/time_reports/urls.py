from django.urls import path
from . import views

app_name = 'time_reports'
urlpatterns = [
    # path('', views.EmployeeList.as_view(), name='employee-list', kwargs={'all': False}),
    # path('all/', views.EmployeeList.as_view(), name='employee-list-all', kwargs={'all': True}),
    # path('new/', views.EmployeeCreate.as_view(), name='employee-create'),
    # path('api/', views.EmployeeAutocomplete.as_view(), name='employee-autocomplete'),
    # path('<slug:slug>/', views.EmployeeDetail.as_view(), name='employee-detail'),
    # path('<slug:slug>/edit', views.EmployeeUpdate.as_view(), name='employee-update'),
    # path('<slug:slug>/deactivate', views.EmployeeDeactivate.as_view(), name='employee-deactivate'),
    # path('<slug:slug>/activate', views.EmployeeActivate.as_view(), name='employee-activate'),
    # path('<slug:slug>/contract/new', views.ContractCreate.as_view(), name='contract-create'),
    # path('<slug:employee>/contract/<int:pk>', views.ContractDetail.as_view(), name='contract-detail'),
    # path('<slug:employee>/contract/<int:pk>/edit', views.ContractUpdate.as_view(), name='contract-update'),
    # path('<slug:employee>/contract/<int:pk>/delete', views.ContractDelete.as_view(), name='contract-delete'),
    # path('<slug:slug>/rate/new', views.RateCreate.as_view(), name='rate-create'),
    # path('<slug:employee>/rate/<int:pk>', views.RateDetail.as_view(), name='rate-detail'),
    # path('<slug:employee>/rate/<int:pk>/edit', views.RateUpdate.as_view(), name='rate-update'),
    # path('<slug:employee>/rate/<int:pk>/delete', views.RateDelete.as_view(), name='rate-delete'),
    path('', views.TimeReportList.as_view(), name='time-report-list'),
    path('new/', views.TimeReportCreate.as_view(), name='time-report-create'),
    path('<int:pk>/', views.TimeReportDetail.as_view(), name='time-report-detail'),
    # path('<int:pk>/edit', views.edit_time_report, name='time-report-update'),
    path('<int:pk>/edit', views.TimeReportUpdate.as_view(), name='time-report-update'),
    # path('approvals/', views.ApprovalsList.as_view(), name='approval-list'),
    # path('approvals/<str:type>/<int:pk>/approve', views.ApprovalDecision.as_view(), name='approval-approve', kwargs={'decision': 'approve'}),
    # path('approvals/<str:type>/<int:pk>/reject', views.ApprovalDecision.as_view(), name='approval-reject', kwargs={'decision': 'reject'}),

    
]
