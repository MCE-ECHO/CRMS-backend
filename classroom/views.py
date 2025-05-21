from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import Classroom, Block
from .serializers import ClassroomSerializer, BlockSerializer
from timetable.models import Timetable
from accounts.utils import is_admin
from datetime import datetime
from django import forms

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
@permission_classes([IsAdminUser])
def classroom_list(request):
    """
    List all classrooms with block info.
    """
    classrooms = Classroom.objects.select_related('block').all()
    serializer = ClassroomSerializer(classrooms, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
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
