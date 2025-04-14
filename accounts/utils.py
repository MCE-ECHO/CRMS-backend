def is_teacher(user):
    return hasattr(user, 'teacherprofile')

def is_admin(user):
    return user.is_staff or user.is_superuser
