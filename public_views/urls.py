from django.urls import path
from .views import student_timetable_view, student_available_classrooms, student_portal

urlpatterns = [
    path('timetable/', student_timetable_view, name='public-timetable'),
    path('available-classrooms/', student_available_classrooms, name='public-available-classrooms'),
    path('portal/', student_portal, name='public-student-portal'),
]
