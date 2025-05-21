from django.urls import path
from .views import all_timetables, add_timetable, update_timetable, delete_timetable, export_timetable

app_name = 'timetable'

urlpatterns = [
    path('api/all/', all_timetables, name='api-all-timetables'),
    path('api/add/', add_timetable, name='api-add-timetable'),
    path('api/update/<int:pk>/', update_timetable, name='api-update-timetable'),
    path('api/delete/<int:pk>/', delete_timetable, name='api-delete-timetable'),
    path('api/export/', export_timetable, name='api-export-timetable'),
]
