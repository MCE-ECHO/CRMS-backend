from django.shortcuts import render
from django.http import JsonResponse
from timetable.models import Timetable
from classroom.models import Classroom
from datetime import datetime
from django.db.models import Q

def student_portal(request):
    return render(request, 'public_views/student_portal.html')

def student_timetable_view(request):
    classroom_name = request.GET.get('classroom')
    if not classroom_name:
        return JsonResponse({'error': 'Classroom name is required'}, status=400)

    try:
        classroom = Classroom.objects.get(name__icontains=classroom_name)
        timetable = Timetable.objects.filter(classroom=classroom).select_related('teacher')
        data = [{
            'day': entry.day,
            'start_time': entry.start_time.strftime('%H:%M'),
            'end_time': entry.end_time.strftime('%H:%M'),
            'teacher': entry.teacher.username if entry.teacher else 'N/A'
        } for entry in timetable]
        return JsonResponse(data, safe=False)
    except Classroom.DoesNotExist:
        return JsonResponse({'error': 'Classroom not found'}, status=404)

def student_available_classrooms(request):
    date = request.GET.get('date')
    start = request.GET.get('start_time')
    end = request.GET.get('end_time')
    block = request.GET.get('block')

    try:
        start_time = datetime.strptime(start, "%H:%M").time()
        end_time = datetime.strptime(end, "%H:%M").time()
        search_date = datetime.strptime(date, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid time/date format'}, status=400)

    booked_ids = Timetable.objects.filter(
        day=search_date.strftime('%A'),
        start_time__lt=end_time,
        end_time__gt=start_time
    ).values_list('classroom_id', flat=True)

    query = Q(id__not_in=booked_ids)
    if block:
        query &= Q(block__name__icontains=block)

    classrooms = Classroom.objects.filter(query).select_related('block')
    data = [{'name': c.name, 'block': c.block.name} for c in classrooms]
    return JsonResponse(data, safe=False)
