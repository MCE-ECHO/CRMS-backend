from django.urls import path
from .views import TeacherTimetableView

urlpatterns = [
    path('teacher/<int:user_id>/timetable/', TeacherTimetableView.as_view(), name='teacher-timetable'),
]
