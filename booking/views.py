from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Booking
from .serializers import BookingSerializer

class BookingListCreateView(APIView):
    def get(self, request):
        bookings = Booking.objects.all().select_related('user', 'classroom')
        serializer = BookingSerializer(bookings, many=True)
        return Response(serializer.data)
