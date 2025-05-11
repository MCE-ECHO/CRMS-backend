from django.urls import path
from .views import (
    booking_create_view,
    booking_list_view,
    BookingListView,
    approve_booking,
    reject_booking,
)

app_name = 'booking'

urlpatterns = [
    path('create/', booking_create_view, name='booking-create'),
    path('list/', booking_list_view, name='booking-list'),
    path('admin/list/', BookingListView.as_view(), name='admin-booking-list'),
    path('admin/approve/<int:pk>/', approve_booking, name='approve-booking'),
    path('admin/reject/<int:pk>/', reject_booking, name='reject-booking'),
]
