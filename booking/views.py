from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
from .serializers import BookingSerializer
from django.shortcuts import get_object_or_404

class BookingListCreateView(APIView):
    """
    API view to list all bookings or create a new booking.
    """

    def get(self, request):
        bookings = Booking.objects.all().select_related('user', 'classroom')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            classroom = serializer.validated_data['classroom']
            date = serializer.validated_data['date']
            start_time = serializer.validated_data['start_time']
            end_time = serializer.validated_data['end_time']

            # Check for booking conflicts
            conflicts = Booking.objects.filter(
                classroom=classroom,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
                status='approved'
            )
            if conflicts.exists():
                return Response({'error': 'This time slot is already booked.'}, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApproveBookingView(APIView):
    """
    API view to approve a booking by its primary key.
    """

    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.status = 'approved'
        booking.save()
        return Response({'status': 'Booking approved'})

