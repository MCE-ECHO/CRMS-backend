from rest_framework import serializers
from .models import Timetable

class TimetableSerializer(serializers.ModelSerializer):
    teacher = serializers.ReadOnlyField(source='teacher.username')
    classroom = serializers.ReadOnlyField(source='classroom.name')

    class Meta:
        model = Timetable
        fields = '__all__'

