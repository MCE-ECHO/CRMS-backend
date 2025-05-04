from django.db import models
from django.contrib.auth.models import User
from classroom.models import Classroom

class Timetable(models.Model):
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.classroom.name} - {self.day} {self.start_time}-{self.end_time}"
