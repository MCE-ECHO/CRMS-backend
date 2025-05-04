from rest_framework import serializers
from .models import Booking

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    classroom = serializers.ReadOnlyField(source='classroom.name')

    class Meta:
        model = Booking
        fields = '__all__'
