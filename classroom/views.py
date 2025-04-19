from django.shortcuts import render
from .models import Classroom

def classroom_list(request):
    """
    View to display a list of all classrooms with their associated blocks.
    """
    classrooms = Classroom.objects.all().select_related('block')
    return render(request, 'classroom/classroom_list.html', {'classrooms': classrooms})

