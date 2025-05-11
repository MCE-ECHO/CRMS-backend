from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import Booking
from .serializers import BookingSerializer
from accounts.utils import is_admin
from accounts.forms import BookingForm  # Corrected import

@login_required
def booking_create_view(request):
    """
    Handle booking creation with form validation and conflict checking.
    Only logged-in users can create bookings, with classroom filtering based on user role.
    """
    if request.method == 'POST':
        form = BookingForm(request.POST, user=request.user)  # Pass user for classroom filtering
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            # Check for conflicting bookings
            conflicts = Booking.objects.filter(
                classroom=booking.classroom,
                date=booking.date,
                start_time__lt=booking.end_time,
                end_time__gt=booking.start_time,
                status='approved'
            )
            if conflicts.exists():
                messages.error(request, 'This classroom is already booked for the selected time.')
            else:
                # Set status based on user role (auto-approve for teachers)
                booking.status = 'approved' if request.user.is_staff else 'pending'
                booking.save()
                messages.success(request, 'Booking request submitted successfully.')
                return redirect('booking:booking-list')
        else:
            messages.error(request, 'Error creating booking. Please check the form.')
    else:
        form = BookingForm(user=request.user)  # Pass user for initial form
    return render(request, 'booking/booking_form.html', {'form': form})

@login_required
def booking_list_view(request):
    """
    Display a list of bookings for the current user.
    """
    bookings = Booking.objects.filter(user=request.user).select_related('classroom')
    return render(request, 'booking/booking_list.html', {'bookings': bookings})

class BookingListView(APIView):
    """
    API endpoint for admins to view all bookings.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        bookings = Booking.objects.select_related('user', 'classroom').all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

@api_view(['POST'])
@user_passes_test(is_admin)
def approve_booking(request, pk):
    """
    API endpoint for admins to approve a booking.
    """
    try:
        booking = Booking.objects.get(pk=pk)
        booking.status = 'approved'
        booking.save()
        return Response({'message': 'Booking approved'}, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@user_passes_test(is_admin)
def reject_booking(request, pk):
    """
    API endpoint for admins to reject a booking.
    """
    try:
        booking = Booking.objects.get(pk=pk)
        booking.status = 'rejected'
        booking.save()
        return Response({'message': 'Booking rejected'}, status=status.HTTP_200_OK)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
