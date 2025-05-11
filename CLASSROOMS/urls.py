from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home_redirect_view
from django.contrib.auth import views as auth_views
from CLASSROOMS.views import toggle_dark_mode  # <-- Add this import

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('admin-dashboard/', include('admin_dashboard.urls', namespace='admin_dashboard')),
    path('public/', include('public_views.urls', namespace='public_views')),
    path('classrooms/', include('classroom.urls', namespace='classroom')),
    path('timetable/', include('timetable.urls', namespace='timetable')),
    path('booking/', include('booking.urls', namespace='booking')),
    path('', home_redirect_view, name='home'),
    path('toggle-dark-mode/', toggle_dark_mode, name='toggle_dark_mode'),  # <-- Add this line
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

