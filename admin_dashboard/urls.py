from django.urls import path
from .views import (
    admin_dashboard_view,
    TimetableUploadView,
    UsageStatsView,
    PeakHoursView,
    ActiveFacultyView,
    PendingBookingsView,
    approve_booking,
    reject_booking,
    available_classrooms,
    all_timetables,
    add_timetable,
    update_timetable,
    delete_timetable,
    classroom_list,
    teacher_list,
    export_timetable_csv
)

urlpatterns = [
    # Dashboard
    path('', admin_dashboard_view, name='admin-dashboard'),

    # File Upload
    path('upload-timetable/', TimetableUploadView.as_view(), name='upload-timetable'),

    # Statistics
    path('usage/', UsageStatsView.as_view(), name='usage-stats'),
    path('peak-hours/', PeakHoursView.as_view(), name='peak-hours'),
    path('active-faculty/', ActiveFacultyView.as_view(), name='active-faculty'),

    # Bookings Management
    path('pending-bookings/', PendingBookingsView.as_view(), name='pending-bookings'),
    path('approve-booking/<int:booking_id>/', approve_booking, name='approve-booking'),
    path('reject-booking/<int:booking_id>/', reject_booking, name='reject-booking'),

    # Classroom Availability
    path('available-classrooms/', available_classrooms, name='available-classrooms'),

    # Timetable Management
    path('timetable/', all_timetables, name='all-timetables'),
    path('timetable/add/', add_timetable, name='add-timetable'),
    path('timetable/update/<int:pk>/', update_timetable, name='update-timetable'),
    path('timetable/delete/<int:pk>/', delete_timetable, name='delete-timetable'),
    path('timetable/export/', export_timetable_csv, name='export-timetable-csv'),

    # Dropdown Data
    path('classrooms/', classroom_list, name='classroom-list'),
    path('teachers/', teacher_list, name='teacher-list'),
]

