from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import TeacherProfile, StudentProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.is_staff:
            TeacherProfile.objects.create(user=instance)
        else:
            StudentProfile.objects.create(user=instance)
