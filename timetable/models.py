from django.db import models
from classroom.models import Classroom
from django.contrib.auth.models import User

class Batch(models.Model):
    branch = models.CharField(max_length=50)
    semester = models.CharField(max_length=20)
    section = models.CharField(max_length=10, blank=True)

    def __str__(self):
        return f"{self.branch} {self.semester} {self.section}".strip()

class Timetable(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )
    batch = models.ForeignKey('Batch', on_delete=models.CASCADE, related_name='timetables')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    day = models.CharField(max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"{self.batch} | {self.classroom.name} - {self.day} {self.start_time}-{self.end_time}"
