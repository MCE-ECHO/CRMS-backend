from django.db import models
from django.contrib.auth.models import User
from classroom.models import Classroom
from django.core.exceptions import ValidationError

class Timetable(models.Model):
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_name = models.CharField(max_length=100, blank=True, null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    block_name = models.CharField(max_length=50, blank=True, null=True)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")
        conflicts = Timetable.objects.filter(
            classroom=self.classroom,
            day=self.day,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        ).exclude(id=self.id)
        if conflicts.exists():
            raise ValidationError("This time slot is already booked for this classroom.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.day} - {self.start_time} - {self.end_time} - {self.classroom} - {self.teacher}"
