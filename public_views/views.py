from django.shortcuts import render
from django.http import JsonResponse
from timetable.models import Timetable
from classroom.models import Classroom
from datetime import datetime

def student_timetable_view(request):
    # Public view for timetable by classroom
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

def student_available_classrooms(request):
    # Public view for available classrooms
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

    if search_date < datetime.now().date():
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

def student_portal(request):
    # Public student portal page
    return render(request, 'public_views/student_portal.html')
