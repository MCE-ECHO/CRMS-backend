from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Classroom, Block
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
@user_passes_test(is_admin)
def classroom_list(request):
    data = [{'id': c.id, 'name': c.name, 'block': c.block.name} for c in Classroom.objects.select_related('block')]
    return Response(data)

@api_view(['GET'])
@user_passes_test(is_admin)
def available_classrooms(request):
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
    return Response([{'id': c.id, 'name': c.name, 'block': c.block.name} for c in classrooms])
