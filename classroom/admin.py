from django.contrib import admin
from .models import Block, Classroom

@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('name', 'block', 'capacity', 'status')
    list_filter = ('block', 'status')
    search_fields = ('name', 'block__name')
    list_editable = ('status',)  # Allows status to be changed directly in the list view

