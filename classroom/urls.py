from django.urls import path
from . import views

urlpatterns = [
    path('', views.classroom_list, name='classroom-list'),
]
