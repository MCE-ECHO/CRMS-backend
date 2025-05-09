from django.urls import path
from .views import (
    timetable_create_view,
    timetable_list_view,
    TimetableUploadView,
    all_timetables,
    add_timetable,
    update_timetable,
    delete_timetable
)

app_name = 'timetable'

urlpatterns = [
    path('create/', timetable_create_view, name='timetable-create'),
    path('list/', timetable_list_view, name='timetable-list'),
    path('upload/', TimetableUploadView.as_view(), name='timetable-upload'),
    path('api/all/', all_timetables, name='all-timetables'),
    path('api/add/', add_timetable, name='add-timetable'),
    path('api/update/<int:pk>/', update_timetable, name='update-timetable'),
    path('api/delete/<int:pk>/', delete_timetable, name='delete-timetable'),
]

