from django.urls import path
from .views import (
    timetable_view,
    all_timetables,
    add_timetable,
    update_timetable,
    delete_timetable,
    export_timetable,
    upload_timetable,
)

app_name = 'timetable'

urlpatterns = [
    path('', timetable_view, name='timetable-view'),  # Web page for timetable (teacher)
    path('api/all/', all_timetables, name='api-all-timetables'),  # List/filter timetables
    path('api/add/', add_timetable, name='api-add-timetable'),    # Add timetable entry
    path('api/update/<int:pk>/', update_timetable, name='api-update-timetable'),  # Update entry
    path('api/delete/<int:pk>/', delete_timetable, name='api-delete-timetable'),  # Delete entry
    path('api/export/', export_timetable, name='api-export-timetable'),           # Export as CSV
    path('api/upload/', upload_timetable, name='api-upload-timetable'),
]
