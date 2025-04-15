from django.urls import path
from .views import (
    teacher_dashboard,
    student_timetable_view,
    student_available_classrooms,
    student_portal,
    profile_view,
    booking_create_view,
)

urlpatterns = [
    path('teacher/dashboard/', teacher_dashboard, name='teacher-dashboard'),
    path('student/timetable/', student_timetable_view, name='student-timetable'),
    path('student/available-classrooms/', student_available_classrooms, name='student-available-classrooms'),
    path('student/portal/', student_portal, name='student-portal'),
    path('profile/', profile_view, name='profile'),
    path('booking/create/', booking_create_view, name='booking-create'),
]
