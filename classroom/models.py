from django.db import models

class Block(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='classrooms')
    capacity = models.PositiveIntegerField(default=30)  # Added: room capacity
    status = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Free'),
            ('occupied', 'Occupied'),
            ('maintenance', 'Maintenance'),
        ],
        default='free'
    )  # Added: room status

    def __str__(self):
        return self.name
