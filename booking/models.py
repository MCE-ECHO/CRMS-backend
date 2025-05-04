from django.db import models
from django.contrib.auth.models import User
from classroom.models import Classroom
from django.core.exceptions import ValidationError

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError('End time must be after start time.')
        bookings = Booking.objects.filter(
            classroom=self.classroom,
            date=self.date,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
            status='approved'
        ).exclude(id=self.id)
        if bookings.exists():
            raise ValidationError('This classroom is already booked.')

    def __str__(self):
        return f"{self.classroom.name} - {self.date} {self.start_time}-{self.end_time}"
