from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from django.core.files.storage import default_storage
import csv
from django.http import HttpResponse
from .models import Timetable, Batch
from classroom.models import Classroom, Block  # Make sure Block is imported
from django.contrib.auth.models import User
from .serializers import TimetableSerializer

@login_required
def timetable_view(request):
    entries = Timetable.objects.filter(teacher=request.user).select_related('classroom')
    return render(request, 'timetable/timetable.html', {'entries': entries})

@api_view(['GET'])
@permission_classes([AllowAny])
def all_timetables(request):
    """
    List all timetable entries, with optional filters: classroom, block, day, teacher.
    """
    entries = Timetable.objects.select_related('classroom', 'teacher', 'batch').all()
    classroom = request.GET.get('classroom')
    block = request.GET.get('block')
    day = request.GET.get('day')
    teacher = request.GET.get('teacher')
    branch = request.GET.get('branch')
    semester = request.GET.get('semester')
    section = request.GET.get('section')
    batch = request.GET.get('batch')  # batch id

    if classroom:
        entries = entries.filter(classroom__name__icontains=classroom)
    if block:
        entries = entries.filter(classroom__block__name__icontains=block)
    if day:
        entries = entries.filter(day=day)
    if teacher:
        entries = entries.filter(teacher__username__icontains=teacher)
    if branch:
        entries = entries.filter(batch__branch__icontains=branch)
    if semester:
        entries = entries.filter(batch__semester__icontains=semester)
    if section:
        entries = entries.filter(batch__section__icontains=section)
    if batch:
        entries = entries.filter(batch__id=batch)

    serializer = TimetableSerializer(entries, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_timetable(request):
    serializer = TimetableSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def delete_timetable(request, pk):
    try:
        timetable = Timetable.objects.get(pk=pk)
        timetable.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Timetable.DoesNotExist:
        return Response({'error': 'Timetable not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
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

@api_view(['POST'])
@permission_classes([AllowAny])  # or [IsAdminUser] for admin-only
def upload_timetable(request):
    """
    Upload timetable entries from a CSV file.
    Auto-creates missing blocks, classrooms, teachers, and batches.
    """
    file = request.FILES.get('file')
    if not file:
        return Response({'error': 'No file uploaded.'}, status=400)
    decoded_file = file.read().decode('utf-8').splitlines()
    reader = csv.DictReader(decoded_file)
    created = 0
    errors = []
    for idx, row in enumerate(reader, start=2):
        try:
            # Get or create Batch
            batch, _ = Batch.objects.get_or_create(
                branch=row['branch'].strip(),
                semester=row['semester'].strip(),
                section=row['section'].strip()
            )
            # Get or create Block (if block column exists)
            block_obj = None
            block_name = row.get('block', '').strip()
            if block_name:
                block_obj, _ = Block.objects.get_or_create(name=block_name)
            # Get or create Classroom (assign block if available)
            classroom_name = row['classroom'].strip()
            if block_obj:
                classroom, _ = Classroom.objects.get_or_create(
                    name=classroom_name,
                    defaults={'block': block_obj}
                )
                # If classroom exists but block is missing, update it
                if classroom.block != block_obj:
                    classroom.block = block_obj
                    classroom.save()
            else:
                classroom, _ = Classroom.objects.get_or_create(name=classroom_name)
            # Get or create Teacher
            teacher, _ = User.objects.get_or_create(
                username=row['teacher'].strip(),
                defaults={'first_name': '', 'last_name': '', 'email': ''}
            )
            # Create Timetable entry
            Timetable.objects.create(
                batch=batch,
                classroom=classroom,
                teacher=teacher,
                day=row['day'].strip(),
                start_time=row['start_time'].strip(),
                end_time=row['end_time'].strip(),
                subject_name=row.get('subject_name', '').strip()
            )
            created += 1
        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")
    result = {'created': created}
    if errors:
        result['errors'] = errors
    return Response(result, status=201 if created else 400)
