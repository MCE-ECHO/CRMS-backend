from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Timetable
from .serializers import TimetableSerializer

class TeacherTimetableView(APIView):
    def get(self, request, user_id):
        timetable = Timetable.objects.filter(user_id=user_id)
        serializer = TimetableSerializer(timetable, many=True)
        return Response(serializer.data)
