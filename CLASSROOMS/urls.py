"""
URL configuration for CLASSROOMS project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from accounts.views import home_redirect_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Django admin
    path('admin/', admin.site.urls),

    # Auth routes (login/logout) - use Django's built-in or your own
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # App routes with namespace for reverse lookups
    path('accounts/', include('accounts.urls', namespace='accounts')),             # Login, signup, profile, etc.
    path('admin-dashboard/', include('admin_dashboard.urls', namespace='admin_dashboard')),
    path('public/', include('public_views.urls', namespace='public_views')),       # Student/public views
    path('classrooms/', include('classroom.urls', namespace='classroom')),         # Classroom CRUD/viewing
    path('timetable/', include('timetable.urls', namespace='timetable')),          # Timetables
    path('booking/', include('booking.urls', namespace='booking')),                # Room bookings

    # Home/landing page (auto-redirects based on user type)
    path('', home_redirect_view, name='home'),
]

# Static and media serving for development only
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

