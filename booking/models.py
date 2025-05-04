from django.db import models
from django.contrib.auth.models import User
from classroom.models import Classroom
from django.core.exceptions import ValidationError
from django.utils import timezone

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
        # Validate booking times and date
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        if self.date and self.date < timezone.now().date():
            raise ValidationError("Booking date cannot be in the past.")
        # Check for conflicts with existing bookings or timetable
        conflicts = Booking.objects.filter(
            classroom=self.classroom,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status='approved'
        ).exclude(id=self.id)
        if conflicts.exists():
            raise ValidationError("This classroom is already booked for the selected time.")
        timetable_conflicts = Timetable.objects.filter(
            classroom=self.classroom,
            day=self.date.strftime('%A'),
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )
        if timetable_conflicts.exists():
            raise ValidationError("This classroom is scheduled in the timetable for the selected time.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.classroom.name} booking by {self.user.username} on {self.date}"
