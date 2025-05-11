from django.db import models
from django.contrib.auth.models import User

class TeacherProfile(models.Model):
    ROLE_CHOICES = [
        ('lecturer', 'Lecturer'),
        ('professor', 'Professor'),
        ('assistant', 'Teaching Assistant'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacherprofile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='lecturer')

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = 'Teacher Profile'
        ordering = ['user__username']

class StudentProfile(models.Model):
    ROLE_CHOICES = [
        ('undergrad', 'Undergraduate'),
        ('postgrad', 'Postgraduate'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentprofile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='undergrad')

    def __str__(self):
        return self.user.get_full_name() or self.user.username

    class Meta:
        verbose_name = 'Student Profile'
        ordering = ['user__username']

class Event(models.Model):
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
