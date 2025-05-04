from django.contrib import admin
from django.utils.html import format_html
from timetable.models import Timetable
from classroom.models import Classroom, Block

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_per_page = 50

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('day', 'formatted_time', 'classroom', 'teacher', 'subject_name')
    list_filter = ('day', 'classroom__block', 'teacher')
    search_fields = ('day', 'classroom__name', 'teacher__username', 'subject_name')
    autocomplete_fields = ['classroom', 'teacher']
    ordering = ('day', 'start_time')
    list_per_page = 50

    def formatted_time(self, obj):
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    formatted_time.short_description = 'Time Slot'

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'block', 'capacity', 'status', 'status_badge')
    list_filter = ('block', 'status')
    search_fields = ('name', 'block__name')
    list_editable = ('status',)
    list_per_page = 50

    def status_badge(self, obj):
        color = 'green' if obj.status == 'free' else 'red' if obj.status == 'occupied' else 'orange'
        display_text = obj.get_status_display()  # Uses choices' human-readable name
        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 8px; border-radius: 4px;">{}</span>',
            color,
            display_text
        )
    status_badge.short_description = 'Status'
