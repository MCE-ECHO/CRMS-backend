from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from accounts.views import home_redirect_view

urlpatterns = [
    # Root URL
    path('', home_redirect_view, name='home'),

    # Admin URL
    path('admin/', admin.site.urls),

    # App routes
    path('accounts/', include('accounts.urls')),
    path('classrooms/', include('classroom.urls')),
    path('timetable/', include('timetable.urls')),
    path('booking/', include('booking.urls')),
    path('admin-dashboard/', include('admin_dashboard.urls')),

    # Authentication routes
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # Specify the template_name
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
]

