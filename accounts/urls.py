from django.urls import path
from .views import (
    teacher_dashboard,
    profile_view,
    booking_create_view,  # Added for booking creation
)
app_name='accounts' #Define the namespace
urlpatterns = [
    path('teacher/dashboard/', teacher_dashboard, name='teacher-dashboard'),
    path('profile/', profile_view, name='profile'),
    path('booking/create/', booking_create_view, name='booking-create'),
]
