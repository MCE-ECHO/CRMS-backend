from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib import messages
from django import forms
from timetable.models import Timetable
from classroom.models import Classroom
from booking.models import Booking
from .utils import is_teacher, is_admin
from .models import TeacherProfile, StudentProfile

# Profile forms
class ProfileForm(forms.ModelForm):
    class Meta:
        model = TeacherProfile
        fields = ['department', 'avatar', 'phone', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
        }

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['roll_number', 'avatar', 'phone', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'w-full p-2 border rounded'}),
        }

def home_redirect_view(request):
    # Redirect users based on their role
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin-dashboard')
        elif is_teacher(request.user):
            return redirect('teacher-dashboard')
        else:
            return redirect('public-student-portal')
    return render(request, 'home.html')

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    # Teacher dashboard view
    profile = request.user.teacherprofile
    timetable = Timetable.objects.filter(teacher=request.user).select_related('classroom')
    bookings = Booking.objects.filter(user=request.user).select_related('classroom')
    classrooms = Classroom.objects.all().select_related('block')  # For booking form
    return render(request, 'accounts/teacher_dashboard.html', {
        'profile': profile,
        'timetable': timetable,
        'bookings': bookings,
        'classrooms': classrooms,
    })

@login_required
def profile_view(request):
    # Profile view for both teachers and students
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
            return redirect('profile')
    else:
        form = form_class(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})

@login_required
@user_passes_test(is_teacher)
@require_POST
def booking_create_view(request):
    # Handle classroom booking creation by teachers
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
        booking.clean()  # Validate the booking
        booking.save()
        messages.success(request, 'Booking request submitted successfully.')
    except Exception as e:
        messages.error(request, f'Error creating booking: {str(e)}')
    return redirect('teacher-dashboard')
