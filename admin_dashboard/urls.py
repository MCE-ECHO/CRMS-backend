from django.urls import path
from .views import (
    admin_dashboard_view, event_create_view, event_list_view, UsageStatsView, PeakHoursView, ActiveFacultyView,
    TimetableUploadView, all_timetables, add_timetable, update_timetable, delete_timetable,
    available_classrooms, classroom_list, teacher_list, export_timetable_csv, BookingListView,
    approve_booking, reject_booking, timetable_management, booking_management, event_management, upload_timetable
)

app_name = 'admin_dashboard'

urlpatterns = [
    path('', admin_dashboard_view, name='admin-dashboard'),
    path('event/create/', event_create_view, name='event-create'),
    path('event/list/', event_list_view, name='event-list'),
    path('event-management/', event_management, name='event-management'),

    path('upload/', TimetableUploadView.as_view(), name='timetable-upload'),
    path('upload-timetable/', upload_timetable, name='upload-timetable'),
    path('timetables/', all_timetables, name='all-timetables'),
    path('timetable/add/', add_timetable, name='add-timetable'),
    path('timetable/update/<int:pk>/', update_timetable, name='update-timetable'),
    path('timetable/delete/<int:pk>/', delete_timetable, name='delete-timetable'),

    path('usage/', UsageStatsView.as_view(), name='usage-stats'),
    path('peak-hours/', PeakHoursView.as_view(), name='peak-hours'),
    path('active-faculty/', ActiveFacultyView.as_view(), name='active-faculty'),

    path('available-classrooms/', available_classrooms, name='available-classrooms'),
    path('classrooms/', classroom_list, name='classroom-list'),
    path('teachers/', teacher_list, name='teacher-list'),

    path('bookings/', BookingListView.as_view(), name='booking-list'),
    path('booking/approve/<int:pk>/', approve_booking, name='approve-booking'),
    path('booking/reject/<int:pk>/', reject_booking, name='reject-booking'),
    path('booking-management/', booking_management, name='booking-management'),

    path('timetable-management/', timetable_management, name='timetable-management'),
    path('export/csv/', export_timetable_csv, name='export-timetable-csv'),
]

