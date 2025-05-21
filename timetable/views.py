from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
import csv
from django.http import HttpResponse
from .models import Timetable
from .serializers import TimetableSerializer

@login_required
def timetable_view(request):
    entries = Timetable.objects.filter(teacher=request.user).select_related('classroom')
    return render(request, 'timetable/timetable.html', {'entries': entries})

@api_view(['GET'])
def all_timetables(request):
    """
    List all timetable entries.
    """
    entries = Timetable.objects.select_related('classroom', 'teacher').all()
    serializer = TimetableSerializer(entries, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def add_timetable(request):
    serializer = TimetableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_timetable(request, pk):
    try:
        timetable = Timetable.objects.get(pk=pk)
        serializer = TimetableSerializer(timetable, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Timetable.DoesNotExist:
        return Response({'error': 'Timetable not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_timetable(request, pk):
    try:
        timetable = Timetable.objects.get(pk=pk)
        timetable.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Timetable.DoesNotExist:
        return Response({'error': 'Timetable not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_timetable(request):
    """
    Export all timetable entries as CSV.
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="timetable_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Day', 'Start Time', 'End Time', 'Classroom', 'Teacher', 'Subject'])
    for timetable in Timetable.objects.select_related('classroom', 'teacher'):
        writer.writerow([
            timetable.day,
            timetable.start_time.strftime('%H:%M'),
            timetable.end_time.strftime('%H:%M'),
            timetable.classroom.name,
            timetable.teacher.username,
            timetable.subject_name or 'N/A'
        ])
    return response
