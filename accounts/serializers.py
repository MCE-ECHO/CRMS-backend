from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TeacherProfile, StudentProfile, Event

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']

class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = TeacherProfile
        fields = ['id', 'user', 'avatar', 'role']

class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = StudentProfile
        fields = ['id', 'user', 'avatar', 'role']

class EventSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'title', 'start_date', 'end_date', 'visibility', 'created_by', 'created_at']
