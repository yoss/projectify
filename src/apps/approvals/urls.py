from django.urls import path
from . import views

app_name = 'approvals'
urlpatterns = [
    path('', views.ApprovalsList.as_view(), name='approval-list'),
    path('<str:type>/<int:pk>/approve', views.ApprovalDecision.as_view(), name='approval-approve', kwargs={'decision': 'approve'}),
    path('<str:type>/<int:pk>/reject', views.ApprovalDecision.as_view(), name='approval-reject', kwargs={'decision': 'reject'}),   
    path('<str:type>/<int:pk>/detail', views.ApprovalDetails.as_view(), name='approval-detail'),
]
