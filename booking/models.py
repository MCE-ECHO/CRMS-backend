from django.db import models
from django.contrib.auth.models import User
from classroom.models import Classroom
from django.core.exceptions import ValidationError
from django.utils import timezone  # Added missing import

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def clean(self):
        # Validate that end_time is after start_time
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        # Validate that booking date is not in the past
        if self.date and self.date < timezone.now().date():
            raise ValidationError("Booking date cannot be in the past.")

    def save(self, *args, **kwargs):
        # Run full_clean before saving to enforce model validation
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.classroom.name} booking by {self.user.username} on {self.date}"

