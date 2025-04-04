from django.shortcuts import render
from .models import Timetable
# Create your views here.
def timetable_view(request):
    timetable = Timetable.objects.all()
    return render(request,'timetable/timetable.html',{'timetable':timetable})