# accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # DRF API endpoints only
    path('api/teachers/', views.TeacherProfileList.as_view(), name='api-teachers'),
    path('api/students/', views.StudentProfileList.as_view(), name='api-students'),
    path('api/events/', views.EventListCreateView.as_view(), name='api-events'),
    path('api/events/visible/', views.EventByVisibilityView.as_view(), name='api-events-visible'),
]
