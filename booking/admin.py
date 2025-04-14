from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'classroom', 'date', 'start_time', 'end_time', 'status')
    list_filter = ('status', 'date', 'classroom')
    search_fields = ('user__username', 'classroom__name')
    date_hierarchy = 'date'
    ordering = ('-date', 'start_time')
    actions = ['approve_bookings', 'reject_bookings']

    @admin.action(description='Approve selected bookings')
    def approve_bookings(self, request, queryset):
        queryset.update(status='approved')

    @admin.action(description='Reject selected bookings')
    def reject_bookings(self, request, queryset):
        queryset.update(status='rejected')

