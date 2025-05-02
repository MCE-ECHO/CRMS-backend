from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils import timezone
from datetime import datetime
from timetable.models import Timetable
from classroom.models import Classroom
from .utils import is_teacher, is_admin
from .models import TeacherProfile, StudentProfile
from django.contrib import messages
from django import forms
from django.http import HttpResponseForbidden

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
    if request.user.is_authenticated:
        if is_admin(request.user):
            return redirect('admin-dashboard')
        elif is_teacher(request.user):
            return redirect('teacher-dashboard')
        else:
            return redirect('student-portal')
    return render(request, 'home.html')

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    profile = request.user.teacherprofile
    timetable = Timetable.objects.filter(teacher=request.user).select_related('classroom')
    return render(request, 'accounts/teacher_dashboard.html', {
        'profile': profile,
        'timetable': timetable,
    })

@require_GET
def student_timetable_view(request):
    class_name = request.GET.get('classroom')
    if not class_name:
        return JsonResponse({'error': 'Missing classroom parameter'}, status=400)

    entries = Timetable.objects.filter(classroom__name=class_name).select_related('teacher')
    data = [{
        'day': e.day,
        'start_time': e.start_time.strftime('%H:%M'),
        'end_time': e.end_time.strftime('%H:%M'),
        'teacher': e.teacher.username if e.teacher else 'N/A',
    } for e in entries]
    return JsonResponse(data, safe=False)

@require_GET
def student_available_classrooms(request):
    date = request.GET.get('date')
    start = request.GET.get('start_time')
    end = request.GET.get('end_time')
    block = request.GET.get('block')

    try:
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        search_date = datetime.strptime(date, "%Y-%m-%d").date()
    except (ValueError, TypeError) as e:
        return JsonResponse({'error': f'Invalid time/date format: {str(e)}'}, status=400)

    if search_date < timezone.now().date():
        return JsonResponse({'error': 'Date cannot be in the past'}, status=400)

    booked_ids = Timetable.objects.filter(
        day=search_date.strftime('%A'),
        start_time__lt=end_time,
        end_time__gt=start_time
    ).values_list('classroom_id', flat=True)

    available_rooms = Classroom.objects.exclude(id__in=booked_ids).select_related('block')
    if block:
        available_rooms = available_rooms.filter(block__name__icontains=block)

    data = [{'name': c.name, 'block': c.block.name} for c in available_rooms]
    return JsonResponse(data, safe=False)

@login_required
def student_portal(request):
    if is_teacher(request.user) or is_admin(request.user):
        return render(request, 'errors/403.html', {'message': 'Access denied: You are not a student.'}, status=403)
    timetable = Timetable.objects.filter(classroom__timetable__teacher__studentprofile__user=request.user).distinct()
    return render(request, 'accounts/student_portal.html', {
        'timetable': timetable,
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
            return redirect('profile')
    else:
        form = form_class(instance=profile)

    return render(request, 'accounts/profile.html', {'form': form, 'profile': profile})
