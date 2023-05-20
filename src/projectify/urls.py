from django.contrib import admin
from django.urls import path
from django.urls.conf import include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clients/', include('apps.clients.urls')),
    path('sso/', include('apps.sso.urls')),
    path('employees/', include('apps.employees.urls')),
    path('projects/', include('apps.projects.urls')),
    path('time-reports/', include('apps.time_reports.urls')),
    path('approvals/', include('apps.approvals.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)