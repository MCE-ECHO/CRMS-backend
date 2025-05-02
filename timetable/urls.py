from django.urls import path
from .views import TeacherTimetableView, AllTimetableView

urlpatterns = [
    path('teacher/<int:user_id>/', TeacherTimetableView.as_view(), name='teacher-timetable'),
    path('', AllTimetableView.as_view(), name='all-timetables'),
]
