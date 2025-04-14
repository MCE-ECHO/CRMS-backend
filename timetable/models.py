from django.db import models
from django.contrib.auth.models import User
from classroom.models import Classroom

class Timetable(models.Model):
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Modified line

    def __str__(self):
        return f"{self.day} - {self.start_time} - {self.end_time} - {self.classroom} - {self.teacher}"

