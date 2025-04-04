from django.db import models

# Create your models here.
class Timetable(models.Model):
    block_name=models.CharField(max_length=15)
    room_no=models.CharField(max_length=10)
    # day=models.CharField
    course_name=models.CharField(max_length=30)
    faculty=models.CharField(max_length=30)
    start_time=models.TimeField()
    end_time=models.TimeField()
    # def __str__(self):
    #     return 

    # def __unicode__(self):
    #     return 
