from django.urls import path
from .views import test_classroom

urlpatterns = [
    path('', test_classroom, name='classroom-home'),
]
