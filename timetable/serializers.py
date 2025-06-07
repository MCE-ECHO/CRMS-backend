from rest_framework import serializers
from .models import Timetable, Batch
from classroom.models import Classroom
from django.contrib.auth.models import User

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = ['id', 'branch', 'semester', 'section']

class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ['id', 'name', 'block']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

class TimetableSerializer(serializers.ModelSerializer):
    classroom = ClassroomSerializer(read_only=True)
    teacher = UserSerializer(read_only=True)
    batch = BatchSerializer(read_only=True)

    class Meta:
        model = Timetable
        fields = [
            'id', 'batch', 'classroom', 'teacher', 'day',
            'start_time', 'end_time', 'subject_name'
        ]
