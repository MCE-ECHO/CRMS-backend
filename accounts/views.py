from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import TeacherProfile, StudentProfile, Event
from .utils import is_teacher, is_admin
from timetable.models import Timetable
from classroom.models import Classroom
from booking.models import Booking
from .forms import ProfileForm, StudentProfileForm, EventForm

def login_view(request):
    """
    Custom login view with 'next' support and error messages.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next') or request.POST.get('next') or 'home'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
            return render(request, 'accounts/login.html', {'username': username})
    return render(request, 'accounts/login.html', {'next': request.GET.get('next', '')})

@login_required
def profile_view(request):
    """
    Profile view for both teachers and students.
    Teachers: view-only by default; Students: editable.
    """
    if is_teacher(request.user):
        profile = request.user.teacherprofile
        form_class = ProfileForm
        can_edit = False
    else:
        profile = request.user.studentprofile
        form_class = StudentProfileForm
        can_edit = True

    if request.method == 'POST' and can_edit:
        form = form_class(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        form = form_class(instance=profile)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile,
        'can_edit': can_edit,
    })

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """
    Dashboard for teachers: show timetable, bookings, classrooms, and events.
    """
    profile = request.user.teacherprofile
    timetable = Timetable.objects.filter(teacher=request.user).select_related('classroom')
    bookings = Booking.objects.filter(teacher=request.user).select_related('classroom')
    classrooms = Classroom.objects.all()
    events = Event.objects.filter(visibility__in=['public', 'teacher']).order_by('start_date')[:5]

    return render(request, 'accounts/teacher_dashboard.html', {
        'profile': profile,
        'timetable': timetable,
        'bookings': bookings,
        'classrooms': classrooms,
        'events': events,
    })

@login_required
@user_passes_test(is_teacher)
def booking_create_view(request):
    """
    Create a booking for a classroom (teachers only).
    """
    if request.method == 'POST':
        classroom_id = request.POST.get('classroom')
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            classroom = Classroom.objects.get(id=classroom_id)
            # Check for overlapping bookings
            overlap = Booking.objects.filter(
                classroom=classroom,
                date=date,
                start_time__lt=end_time,
                end_time__gt=start_time,
                status__in=['pending', 'approved']
            ).exists()
            if overlap:
                messages.error(request, 'This classroom is already booked for the selected time.')
            else:
                Booking.objects.create(
                    teacher=request.user,
                    classroom=classroom,
                    date=date,
                    start_time=start_time,
                    end_time=end_time,
                    status='pending'
                )
                messages.success(request, 'Booking request submitted.')
        except Classroom.DoesNotExist:
            messages.error(request, 'Invalid classroom selected.')
        return redirect('accounts:teacher-dashboard')
    return redirect('accounts:teacher-dashboard')

@login_required
@user_passes_test(is_teacher)
def event_create_view(request):
    """
    Create an event (teachers only).
    """
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.created_by = request.user
            event.save()
            messages.success(request, 'Event created successfully.')
            return redirect('accounts:teacher-dashboard')
        else:
            messages.error(request, 'Error creating event. Please check the form.')
    else:
        form = EventForm()
    return render(request, 'accounts/event_create.html', {'form': form})

@login_required
def event_list_view(request):
    """
    List events visible to the user.
    """
    if is_admin(request.user):
        events = Event.objects.all()
    elif is_teacher(request.user):
        events = Event.objects.filter(visibility__in=['public', 'teacher'])
    else:
        events = Event.objects.filter(visibility='public')
    return render(request, 'accounts/event_list.html', {'events': events})

def home_redirect_view(request):
    """
    Redirect users to the appropriate dashboard based on their role.
    """
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin_dashboard:admin-dashboard')
        elif is_teacher(request.user):
            return redirect('accounts:teacher-dashboard')
        else:
            return redirect('public_views:public-student-portal')
    return render(request, 'home.html')

