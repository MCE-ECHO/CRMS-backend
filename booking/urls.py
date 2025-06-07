from django.urls import path
from .views import (
    booking_create_view,
    booking_list_view,
    BookingListView,
    UserBookingListView,
    BookingCreateView,
    approve_booking,
    reject_booking,
)

app_name = 'booking'

urlpatterns = [
    # Form-based views
    path('create/', booking_create_view, name='booking-create'),
    path('list/', booking_list_view, name='booking-list'),

    # API endpoints
    path('api/bookings/', BookingCreateView.as_view(), name='api-booking-create'),  # POST for booking request
    path('api/my-bookings/', UserBookingListView.as_view(), name='api-my-bookings'),  # GET for user's bookings
    path('api/admin/bookings/', BookingListView.as_view(), name='api-admin-bookings'),  # GET for all bookings (admin)
    path('api/admin/approve/<int:pk>/', approve_booking, name='api-approve-booking'),  # POST to approve
    path('api/admin/reject/<int:pk>/', reject_booking, name='api-reject-booking'),    # POST to reject
]
