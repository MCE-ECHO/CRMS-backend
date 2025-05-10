from django.contrib import admin
from .models import Timetable

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('day', 'start_time', 'end_time', 'classroom', 'teacher')
    list_filter = ('day', 'classroom')
    search_fields = ('classroom__name', 'teacher__username')
