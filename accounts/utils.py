def is_teacher(user):
    """
    Check if the user has an associated TeacherProfile.
    Returns True if user is a teacher, False otherwise.
    """
    return hasattr(user, 'teacherprofile')


def is_admin(user):
    """
    Check if the user has admin privileges.
    Returns True if user is staff or superuser, False otherwise.
    """
    return user.is_staff or user.is_superuser

