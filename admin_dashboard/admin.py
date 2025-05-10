from django.contrib import admin
from django.utils.html import format_html
from classroom.models import Classroom, Block

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']
    list_per_page = 50

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'block', 'capacity', 'status', 'status_badge')
    list_filter = ('block', 'status')
    search_fields = ('name', 'block__name')
    list_editable = ('status',)
    list_per_page = 50

    def status_badge(self, obj):
        color = (
            'green' if obj.status == 'free'
            else 'red' if obj.status == 'occupied'
            else 'orange'
        )
        display_text = obj.get_status_display()
        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 8px; border-radius: 4px;">{}</span>',
            color,
            display_text
        )
    status_badge.short_description = 'Status'

