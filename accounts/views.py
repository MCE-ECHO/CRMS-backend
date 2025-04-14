from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime

# Import models
from timetable.models import Timetable
from booking.models import Booking
from classroom.models import Classroom

# Import utility functions
from .utils import is_teacher, is_admin

# Home Redirect View
def home_redirect_view(request):
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('/admin-dashboard/')
        elif is_teacher(request.user):
            return redirect('teacher-dashboard')
        else:
            return redirect('student-portal')
    return render(request, 'home.html')  # fallback for not-logged-in users

# Teacher Dashboard View
@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    """
    Teacher dashboard view showing profile, timetable, and approved bookings.
    """
    # Retrieve teacher profile and timetable
    profile = request.user.teacherprofile
    timetable = Timetable.objects.filter(teacher=request.user)

    # Retrieve upcoming approved bookings
    upcoming_bookings = Booking.objects.filter(
        user=request.user, status='approved'
    ).order_by('date', 'start_time')

    # Render the teacher dashboard template
    return render(request, 'accounts/teacher_dashboard.html', {
        'profile': profile,
        'timetable': timetable,
        'bookings': upcoming_bookings
    })

# Student Timetable API Endpoint
@require_GET
def student_timetable_view(request):
    """
    API endpoint for student timetable data.
    Returns JSON of scheduled classes for a classroom.
    """
    # Get the classroom name from the query parameters
    class_name = request.GET.get('classroom')

    # Handle missing classroom parameter
    if not class_name:
        return JsonResponse({'error': 'Missing classroom parameter'}, status=400)

    # Retrieve timetable entries for the specified classroom
    entries = Timetable.objects.filter(classroom__name=class_name)

    # Format timetable data for JSON response
    data = [{
        'day': e.day,
        'start_time': e.start_time.strftime('%H:%M'),
        'end_time': e.end_time.strftime('%H:%M'),
        'teacher': e.teacher.username
    } for e in entries]

    # Return JSON response
    return JsonResponse(data, safe=False)

# Student Available Classrooms API Endpoint
@require_GET
def student_available_classrooms(request):
    """
    API endpoint for available classrooms.
    Returns JSON of classrooms not booked during specified time.
    """
    # Get query parameters
    date = request.GET.get('date')
    start = request.GET.get('start_time')
    end = request.GET.get('end_time')
    block = request.GET.get('block')

    try:
        # Parse time and date parameters
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        search_date = datetime.strptime(date, "%Y-%m-%d").date()
    except (ValueError, TypeError) as e:
        # Handle invalid time or date format
        return JsonResponse({'error': f'Invalid time/date format: {str(e)}'}, status=400)

    # Check if the date is in the past
    if search_date < timezone.now().date():
        return JsonResponse({'error': 'Date cannot be in past'}, status=400)

    # Retrieve IDs of booked classrooms during the specified time
    booked_ids = Booking.objects.filter(
        date=date,
        start_time__lt=end_time,
        end_time__gt=start_time,
        status='approved'
    ).values_list('classroom_id', flat=True)

    # Retrieve available classrooms
    available_rooms = Classroom.objects.exclude(id__in=booked_ids)

    # Filter by block if specified
    if block:
        available_rooms = available_rooms.filter(block__icontains=block)

    # Format available classrooms data for JSON response
    return JsonResponse(
        [{'name': c.name, 'block': c.block} for c in available_rooms],
        safe=False
    )

# Student Portal View
def student_portal(request):
    return render(request, 'accounts/student_portal.html')

