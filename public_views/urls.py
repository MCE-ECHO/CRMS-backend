from django.urls import path
from .views import public_classroom_list

app_name = 'public_views'

urlpatterns = [
    path('api/classrooms/', public_classroom_list, name='public-api-classroom-list'),
]
