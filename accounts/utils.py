from django.contrib.auth.models import User

def is_teacher(user):
    return user.is_authenticated and user.is_staff and hasattr(user, 'teacherprofile')

def is_admin(user):
    return user.is_authenticated and user.is_superuser

