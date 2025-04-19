from django.contrib import admin
from django.utils.html import format_html
from timetable.models import Timetable
from classroom.models import Classroom
from booking.models import Booking

@admin.register(Timetable)
class TimetableAdmin(admin.ModelAdmin):
    list_display = ('day', 'formatted_time', 'classroom', 'teacher', 'subject_name')
    list_filter = ('day', 'classroom__block', 'teacher')
    search_fields = ('day', 'classroom__name', 'teacher__username', 'subject_name')
    autocomplete_fields = ['classroom', 'teacher']
    ordering = ('day', 'start_time')
    list_per_page = 50

    def formatted_time(self, obj):
        """Display formatted start and end time."""
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
        """Show colored badge for classroom status."""
        color = 'green' if obj.status == 'free' else 'red'
        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 8px; border-radius: 4px;">{}</span>',
            color,
            'Available' if obj.status == 'free' else 'Occupied'
        )
    status_badge.short_description = 'Status'

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'classroom', 'formatted_date', 'time_slot', 'status_badge')
    list_filter = ('status', 'date', 'classroom__block')
    search_fields = ('user__username', 'classroom__name')
    raw_id_fields = ('user', 'classroom')
    date_hierarchy = 'date'
    ordering = ('-date', 'start_time')
    actions = ['approve_selected', 'reject_selected']
    list_per_page = 50

    def formatted_date(self, obj):
        """Display formatted booking date."""
        return obj.date.strftime("%b %d, %Y")
    formatted_date.admin_order_field = 'date'
    formatted_date.short_description = 'Date'

    def time_slot(self, obj):
        """Display booking time slot."""
        return f"{obj.start_time.strftime('%H:%M')} - {obj.end_time.strftime('%H:%M')}"
    time_slot.short_description = 'Time Slot'

    def status_badge(self, obj):
        """Show colored badge for booking status."""
        colors = {
            'pending': 'orange',
            'approved': 'green',
            'rejected': 'red',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 8px; border-radius: 4px;">{}</span>',
            color,
            obj.status.capitalize()
        )
    status_badge.short_description = 'Status'

    def approve_selected(self, request, queryset):
        """Admin action to approve selected bookings."""
        updated_count = queryset.update(status='approved')
        self.message_user(request, f"{updated_count} booking(s) approved.")
    approve_selected.short_description = 'Approve selected bookings'

    def reject_selected(self, request, queryset):
        """Admin action to reject selected bookings."""
        updated_count = queryset.update(status='rejected')
        self.message_user(request, f"{updated_count} booking(s) rejected.")
    reject_selected.short_description = 'Reject selected bookings'

