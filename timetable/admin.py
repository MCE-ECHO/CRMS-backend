from django.contrib import admin
from .models import Timetable

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'classroom', 'subject', 'day', 'start_time', 'end_time')
    list_filter = ('teacher', 'classroom', 'day')
    search_fields = ('teacher__username', 'classroom__name', 'subject')
    ordering = ('day', 'start_time')

