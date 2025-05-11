from django.urls import path
from .views import classroom_list_view, classroom_list, available_classrooms

app_name = 'classroom'

urlpatterns = [
    path('list/', classroom_list_view, name='classroom-list'),
    path('api/list/', classroom_list, name='api-classroom-list'),
    path('api/available/', available_classrooms, name='api-available-classrooms'),
]
