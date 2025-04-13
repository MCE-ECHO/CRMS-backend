from django.urls import path
from .views import BookingListCreateView, ApproveBookingView

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list-create'),
    path('approve/<int:booking_id>/', ApproveBookingView.as_view(), name='approve-booking'),
]
