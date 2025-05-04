def is_teacher(user):
    # Check if the user is a teacher
    return hasattr(user, 'teacherprofile') and user.is_authenticated

def is_admin(user):
    # Check if the user is an admin
    return (user.is_staff or user.is_superuser) and user.is_authenticated
