from django.urls import path
from .views import classroom_list, available_classrooms, search_classrooms, classroom_realtime_status

app_name = 'classroom'

urlpatterns = [
    path('api/list/', classroom_list, name='api-classroom-list'),
    path('api/available/', available_classrooms, name='api-available-classrooms'),
    path('api/classrooms/search/', search_classrooms, name='search-classrooms'),
    path('api/realtime-status/', classroom_realtime_status, name='api-classroom-realtime-status'),
]
