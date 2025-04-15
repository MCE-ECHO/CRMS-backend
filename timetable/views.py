from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Timetable
from .serializers import TimetableSerializer
from django.shortcuts import get_object_or_404

class TeacherTimetableView(APIView):
    def get(self, request, user_id):
        teacher = get_object_or_404(User, id=user_id, is_staff=True)
        timetable = Timetable.objects.filter(teacher=teacher).select_related('classroom')
        serializer = TimetableSerializer(timetable, many=True)
        return Response(serializer.data)

class AllTimetableView(APIView):
    def get(self, request):
        timetables = Timetable.objects.all().select_related('classroom', 'teacher')
        serializer = TimetableSerializer(timetables, many=True)
        return Response(serializer.data)
