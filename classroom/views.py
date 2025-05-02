from django.shortcuts import render
from .models import Classroom

def classroom_list(request):
    classrooms = Classroom.objects.all().select_related('block')
    return render(request, 'classroom/classroom_list.html', {'classrooms': classrooms})
