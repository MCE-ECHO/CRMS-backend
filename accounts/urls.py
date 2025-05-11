from django.urls import path
from .views import (
    teacher_dashboard,
    profile_view,
    booking_create_view,
    event_create_view,
    event_list_view,
)

app_name = 'accounts'

urlpatterns = [
    path('teacher/dashboard/', teacher_dashboard, name='teacher-dashboard'),
    path('profile/', profile_view, name='profile'),
    path('booking/create/', booking_create_view, name='booking-create'),
    path('events/create/', event_create_view, name='event-create'),
    path('events/', event_list_view, name='event-list'),
]
