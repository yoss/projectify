from django.urls import path
from . import views

app_name = 'sso'
urlpatterns = [
    path('login/', views.login_page, name='login'),
    path('redirect/', views.sso_redirect, name='redirect'),
    path('logout/', views.sso_logout, name='logout'),
    path('callback/', views.sso_callback, name='callback'),
]
