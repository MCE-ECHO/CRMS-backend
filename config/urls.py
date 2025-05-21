from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('admin-dashboard/', include('admin_dashboard.urls', namespace='admin_dashboard')),
    path('public/', include('public_views.urls', namespace='public_views')),
    path('classrooms/', include('classroom.urls', namespace='classroom')),
    path('timetable/', include('timetable.urls', namespace='timetable')),
    path('booking/', include('booking.urls', namespace='booking')),

    # JWT Auth endpoints for frontend
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

