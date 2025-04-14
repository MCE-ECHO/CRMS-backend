from django.db import models
from django.contrib.auth.models import User
from classroom.models import Classroom

class Timetable(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'is_staff': True}, related_name='timetables')  # Teacher
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='timetables')
    subject = models.CharField(max_length=100)
    day = models.CharField(max_length=10)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.subject} by {self.teacher.username} in {self.classroom.name}"

