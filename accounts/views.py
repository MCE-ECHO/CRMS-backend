from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django import forms
from timetable.models import Timetable
from classroom.models import Classroom
from booking.models import Booking
from .utils import is_teacher, is_admin
from .models import TeacherProfile, StudentProfile, Event
from datetime import datetime

class ProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['department', 'avatar', 'phone']
        widgets = {
            'department': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'avatar', 'phone']
        widgets = {
            'roll_number': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'phone': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_date', 'end_date', 'visibility']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-lg'}),
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-3 border rounded-lg'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'w-full p-3 border rounded-lg'}),
            'visibility': forms.Select(attrs={'class': 'w-full p-3 border rounded-lg'}),
        }

def home_redirect_view(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard:admin-dashboard')
        elif is_teacher(request.user):
            return redirect('accounts:teacher-dashboard')
        else:
            return redirect('public_views:public-student-portal')
    return render(request, 'home.html')

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    profile = request.user.teacherprofile
    if not profile.department:
        timetable = Timetable.objects.filter(teacher=request.user).first()
        if timetable:
            profile.department = timetable.subject_name or 'General'
            profile.save()
    timetable = Timetable.objects.filter(teacher=request.user).select_related('classroom')
    bookings = Booking.objects.filter(user=request.user).select_related('classroom')
    classrooms = Classroom.objects.all().select_related('block')
    events = Event.objects.filter(visibility__in=['public', 'teacher']).order_by('start_date')[:5]
    return render(request, 'accounts/teacher_dashboard.html', {
        'profile': profile,
        'timetable': timetable,
        'bookings': bookings,
        'classrooms': classrooms,
        'events': events,
    })

@login_required
def profile_view(request):
    if is_teacher(request.user):
        profile = request.user.teacherprofile
        form_class = ProfileForm
    else:
        profile = request.user.studentprofile
        form_class = StudentProfileForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = form_class(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

@login_required
@user_passes_test(is_teacher)
def booking_create_view(request):
    if request.method == 'POST':
        try:
            classroom_id = request.POST.get('classroom')
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            classroom = Classroom.objects.get(id=classroom_id)
            booking = Booking(
                user=request.user,
                classroom=classroom,
                date=date,
                start_time=start_time,
                end_time=end_time,
                status='pending'
            )
            booking.clean()
            booking.save()
            messages.success(request, 'Booking request submitted.')
        except Exception as e:
            messages.error(request, f'Error creating booking: {str(e)}')
        return redirect('accounts:teacher-dashboard')
    return redirect('accounts:teacher-dashboard')

@login_required
@user_passes_test(is_teacher)
def event_create_view(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('accounts:teacher-dashboard')
        else:
            messages.error(request, 'Error creating event.')
    else:
        form = EventForm()
    return render(request, 'accounts/event_create.html', {'form': form})

@login_required
def event_list_view(request):
    if is_admin(request.user):
        events = Event.objects.all()
    elif is_teacher(request.user):
        events = Event.objects.filter(visibility__in=['public', 'teacher'])
    else:
        events = Event.objects.filter(visibility='public')
    return render(request, 'accounts/event_list.html', {'events': events})
