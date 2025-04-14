from django.shortcuts import render
from .models import Classroom

def classroom_list(request):
    """
    Display a list of classrooms.
    """
    classrooms = Classroom.objects.all().select_related('block')
    return render(request, 'classroom/classroom_list.html', {'classrooms': classrooms})

