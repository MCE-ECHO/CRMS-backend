from django.db import models
from django.contrib.auth.models import User
from classrooms.models import Classroom

class Timetable(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Teacher
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.subject} by {self.user.username} in {self.classroom.name}"
