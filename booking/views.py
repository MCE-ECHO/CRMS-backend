from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
from .serializers import BookingSerializer
from django.shortcuts import get_object_or_404

class BookingListCreateView(APIView):
    """
    List all bookings, or create a new booking.
    """
    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ApproveBookingView(APIView):
    """
    Approve a booking.
    """
    def post(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk)
        booking.status = 'approved'
        booking.save()
        return Response({'status': 'Booking approved'})

