from rest_framework import serializers
from .models import Booking
from django.contrib.auth.models import User
from classroom.models import Classroom

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name']

class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    classroom = ClassroomSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'classroom', 'date',
            'start_time', 'end_time', 'status', 'created_at'
        ]
