"""
URL configuration for CLASSROOMS project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts.views import home_redirect_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home_redirect_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('classrooms/', include('classroom.urls', namespace='classroom')),
    path('timetable/', include('timetable.urls', namespace='timetable')),
    path('booking/', include('booking.urls', namespace='booking')),
    path('admin-dashboard/', include('admin_dashboard.urls', namespace='admin_dashboard')),
    path('public/', include('public_views.urls', namespace='public_views')),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
