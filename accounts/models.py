from django.db import models
from django.contrib.auth.models import User

class TeacherProfile(models.Model):
    """
    Profile model for teachers, linked one-to-one with Django's User model.
    - avatar: Optional profile image.
    - phone: Optional phone number.
    - bio: Optional short biography/introduction.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacherprofile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)
    bio = models.TextField(max_length=500, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = 'Teacher Profile'
        ordering = ['user__username']


class StudentProfile(models.Model):
    """
    Profile model for students, linked one-to-one with Django's User model.
    - roll_number: Optional student roll number.
    - avatar: Optional profile image.
    - phone: Optional phone number.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentprofile')
    roll_number = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = 'Student Profile'
        ordering = ['user__username']


class Event(models.Model):
    """
    Event model for scheduling and announcements.
    - title: Event name.
    - start_date, end_date: Event duration.
    - visibility: Who can see the event.
    - created_by: User who created the event.
    - created_at: Timestamp of creation.
    """
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('teacher', 'Teachers Only'),
        ('admin', 'Admins Only'),
    ]

    title = models.CharField(max_length=200)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-start_date']

