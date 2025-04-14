from django.urls import path
from .views import (
    teacher_dashboard,
    student_timetable_view,
    student_available_classrooms,
    student_portal
)

urlpatterns = [
    path('teacher/dashboard/', teacher_dashboard, name='teacher-dashboard'),
    path('student/timetable/', student_timetable_view, name='student-timetable'),
    path('student/available-classrooms/', student_available_classrooms, name='student-available-classrooms'),
    path('student/portal/', student_portal, name='student-portal'),
]

