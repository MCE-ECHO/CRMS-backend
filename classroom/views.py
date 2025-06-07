from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Classroom, Block
from .serializers import ClassroomSerializer, BlockSerializer
from timetable.models import Timetable
from accounts.utils import is_admin
from datetime import datetime
from django import forms
from django.utils import timezone
from booking.models import Booking

class ClassroomFilterForm(forms.Form):
    block = forms.ModelChoiceField(
        queryset=Block.objects.all(),
        required=False,
        empty_label="All Blocks",
        widget=forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'})
    )

@login_required
def classroom_list_view(request):
    form = ClassroomFilterForm(request.GET or None)
    classrooms = Classroom.objects.all().select_related('block')
    if form.is_valid() and form.cleaned_data['block']:
        classrooms = classrooms.filter(block=form.cleaned_data['block'])
    return render(request, 'classroom/classroom_list.html', {
        'form': form,
        'classrooms': classrooms
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def classroom_list(request):
    """
    List all classrooms with block info.
    """
    classrooms = Classroom.objects.select_related('block').all()
    serializer = ClassroomSerializer(classrooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def available_classrooms(request):
    """
    List available classrooms for a given date, time range, and optional block.
    """
    date = request.GET.get('date')
    start = request.GET.get('start_time')
    end = request.GET.get('end_time')
    block = request.GET.get('block')
    
    try:
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        search_date = datetime.strptime(date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return Response({'error': 'Invalid time/date format'}, status=status.HTTP_400_BAD_REQUEST)

    booked_ids = Timetable.objects.filter(
        day=search_date.strftime('%A'),
        start_time__lt=end_time,
        end_time__gt=start_time
    ).values_list('classroom_id', flat=True)

    classrooms = Classroom.objects.exclude(id__in=booked_ids).select_related('block')
    if block:
        classrooms = classrooms.filter(block__name__icontains=block)

    serializer = ClassroomSerializer(classrooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])  # Or use IsAdminUser if you want to restrict
def search_classrooms(request):
    """
    Search classrooms by name, block, status, and optionally by availability at a specific date/time.
    Query params: name, block, status, date, start_time, end_time
    """
    qs = Classroom.objects.select_related('block').all()
    name = request.GET.get('name')
    block = request.GET.get('block')
    status = request.GET.get('status')
    date = request.GET.get('date')
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')

    if name:
        qs = qs.filter(name__icontains=name)
    if block:
        qs = qs.filter(block__name__icontains=block)
    if status:
        qs = qs.filter(status=status)

    # Availability filter (optional)
    if date and start_time and end_time:
        try:
            search_date = datetime.strptime(date, "%Y-%m-%d").date()
            start = datetime.strptime(start_time, "%H:%M").time()
            end = datetime.strptime(end_time, "%H:%M").time()
            day_name = search_date.strftime('%A')
            booked_ids = Timetable.objects.filter(
                day=day_name,
                start_time__lt=end,
                end_time__gt=start
            ).values_list('classroom_id', flat=True)
            qs = qs.exclude(id__in=booked_ids)
        except Exception:
            return Response({'error': 'Invalid date or time format'}, status=400)

    serializer = ClassroomSerializer(qs, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def classroom_realtime_status(request):
    """
    Returns a list of classrooms with real-time status: 'free' or 'occupied'
    based on current time, timetable, and approved bookings.
    """
    now = timezone.localtime()
    current_day = now.strftime('%A')
    current_time = now.time()
    classrooms = Classroom.objects.select_related('block').all()
    data = []
    for classroom in classrooms:
        # Check for current timetable
        is_occupied = Timetable.objects.filter(
            classroom=classroom,
            day=current_day,
            start_time__lte=current_time,
            end_time__gt=current_time
        ).exists()
        # Check for current approved booking
        is_occupied = is_occupied or Booking.objects.filter(
            classroom=classroom,
            date=now.date(),
            start_time__lte=current_time,
            end_time__gt=current_time,
            status='approved'
        ).exists()
        data.append({
            'id': classroom.id,
            'name': classroom.name,
            'block': classroom.block.name,
            'status': 'occupied' if is_occupied else 'free'
        })
    return Response(data)
