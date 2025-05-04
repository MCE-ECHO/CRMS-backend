from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Timetable
from .serializers import TimetableSerializer

class TeacherTimetableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        timetable = Timetable.objects.filter(teacher_id=user_id).select_related('classroom')
        serializer = TimetableSerializer(timetable, many=True)
        return Response(serializer.data)

class AllTimetableView(APIView):
    def get(self, request):
        timetable = Timetable.objects.all().select_related('classroom', 'teacher')
        serializer = TimetableSerializer(timetable, many=True)
        return Response(serializer.data)
