from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from .models import Booking
from .serializers import BookingSerializer
from accounts.utils import is_admin

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
    permission_classes = [AllowAny]

    def get(self, request):
        bookings = Booking.objects.select_related('user', 'classroom').all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class UserBookingListView(APIView):
    """
    API endpoint for users to view their own bookings.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        bookings = Booking.objects.filter(user=request.user).select_related('classroom')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

class BookingCreateView(APIView):
    """
    API endpoint for users (including staff) to create a booking request.
    All requests are 'pending' until approved by admin.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            classroom = serializer.validated_data['classroom']
            date = serializer.validated_data['date']
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']
            conflicts = Booking.objects.filter(
                classroom=classroom,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
                status='approved'
            )
            if conflicts.exists():
                return Response({'error': 'This classroom is already booked for the selected time.'}, status=status.HTTP_400_BAD_REQUEST)
            # All requests are pending, even for staff
            booking = serializer.save(
                user=request.user,
                status='pending'
            )
            return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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
