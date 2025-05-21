# accounts/views_api.py
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TeacherProfile, StudentProfile, Event
from accounts.serializers import UserSerializer, TeacherProfileSerializer, StudentProfileSerializer, EventSerializer

class TeacherProfileList(generics.ListAPIView):
    queryset = TeacherProfile.objects.select_related('user').all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class StudentProfileList(generics.ListAPIView):
    queryset = StudentProfile.objects.select_related('user').all()
    serializer_class = StudentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

class EventListCreateView(generics.ListCreateAPIView):
    queryset = Event.objects.select_related('created_by').all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class EventByVisibilityView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.is_superuser:
            events = Event.objects.all()
        elif hasattr(user, 'teacherprofile'):
            events = Event.objects.filter(visibility__in=['public', 'teacher'])
        else:
            events = Event.objects.filter(visibility='public')
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data)
