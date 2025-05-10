from rest_framework import serializers
from .models import Timetable
from classroom.models import Classroom
from django.contrib.auth.models import User

class TimetableSerializer(serializers.ModelSerializer):
    classroom = serializers.SlugRelatedField(slug_field='name', queryset=Classroom.objects.all())
    teacher = serializers.SlugRelatedField(slug_field='username', queryset=User.objects.all())
    start_time = serializers.TimeField(format='%H:%M')
    end_time = serializers.TimeField(format='%H:%M')

    class Meta:
        model = Timetable
        fields = ['id', 'day', 'start_time', 'end_time', 'classroom', 'teacher', 'subject_name']
