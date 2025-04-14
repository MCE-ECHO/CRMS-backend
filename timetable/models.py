from django.db import models
from django.contrib.auth.models import User
from classroom.models import Classroom

class Timetable(models.Model):
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject_name = models.CharField(max_length=100, blank=True, null=True)
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    block_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.day} - {self.start_time} - {self.end_time} - {self.classroom} - {self.teacher}"

