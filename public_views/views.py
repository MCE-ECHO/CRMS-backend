from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from classroom.models import Classroom, Block
from timetable.models import Timetable
from booking.models import Booking
from datetime import datetime
from django import forms

class AvailabilityForm(forms.Form):
    block = forms.ModelChoiceField(
        queryset=Block.objects.all(),
        required=False,
        empty_label="All Blocks",
        widget=forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'})
    )
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'date'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'time'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'w-full p-3 border rounded-lg', 'type': 'time'})
    )

class ClassroomFilterForm(forms.Form):
    block = forms.ModelChoiceField(
        queryset=Block.objects.all(),
        required=False,
        empty_label="All Blocks",
        widget=forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'})
    )

@login_required
def student_portal_view(request):
    bookings = Booking.objects.filter(user=request.user).select_related('classroom').order_by('-created_at')[:5]
    return render(request, 'public_views/student_portal.html', {'bookings': bookings})

@login_required
def classroom_list_view(request):
    form = ClassroomFilterForm(request.GET or None)
    classrooms = Classroom.objects.all().select_related('block')
    if form.is_valid() and form.cleaned_data['block']:
        classrooms = classrooms.filter(block=form.cleaned_data['block'])
    return render(request, 'public_views/classroom_list.html', {
        'form': form,
        'classrooms': classrooms
    })

@login_required
def availability_view(request):
    form = AvailabilityForm(request.GET or None)
    classrooms = []
    if form.is_valid():
        date = form.cleaned_data['date']
        start_time = form.cleaned_data['start_time']
        end_time = form.cleaned_data['end_time']
        block = form.cleaned_data['block']

        booked_ids = set(Timetable.objects.filter(
            day=date.strftime('%A'),
            start_time__lt=end_time,
            end_time__gt=start_time
        ).values_list('classroom_id', flat=True))

        booked_ids.update(Booking.objects.filter(
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time,
            status='approved'
        ).values_list('classroom_id', flat=True))

        classrooms = Classroom.objects.exclude(id__in=booked_ids).select_related('block')
        if block:
            classrooms = classrooms.filter(block=block)

    return render(request, 'public_views/availability.html', {
        'form': form,
        'classrooms': classrooms
    })

@api_view(['GET'])
def public_classroom_list(request):
    data = [{'id': c.id, 'name': c.name, 'block': c.block.name} for c in Classroom.objects.select_related('block')]
    return Response(data)

