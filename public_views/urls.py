from django.urls import path
from .views import (
    student_portal_view,
    classroom_list_view,
    availability_view,
    public_classroom_list,
)

app_name = 'public_views'

urlpatterns = [
    path('student-portal/', student_portal_view, name='public-student-portal'),
    path('classrooms/', classroom_list_view, name='public-classroom-list'),
    path('availability/', availability_view, name='public-availability'),
    path('api/classrooms/', public_classroom_list, name='public-api-classroom-list'),
]

