from rest_framework import serializers
from .models import Booking
from classroom.models import Classroom
from django.contrib.auth.models import User

class BookingSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    classroom = serializers.SlugRelatedField(slug_field='name', queryset=Classroom.objects.all())
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = Booking
        fields = ['id', 'user', 'classroom', 'date', 'start_time', 'end_time', 'status', 'created_at']

