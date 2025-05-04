from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import TeacherProfile, StudentProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    # Automatically create a profile when a user is created
    if created:
        if instance.is_staff or instance.is_superuser:
            TeacherProfile.objects.create(user=instance)
        else:
            StudentProfile.objects.create(user=instance)
