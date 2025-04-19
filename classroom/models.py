from django.db import models

class Block(models.Model):
    """
    Model representing a building block or section where classrooms are located.
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Classroom(models.Model):
    """
    Model representing a classroom within a block.
    """
    STATUS_CHOICES = [
        ('free', 'Free'),
        ('occupied', 'Occupied'),
    ]

    name = models.CharField(max_length=50, unique=True)
    block = models.ForeignKey(Block, on_delete=models.CASCADE, related_name='classrooms')
    capacity = models.IntegerField(default=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='free')

    def __str__(self):
        return f"{self.name} ({self.block.name})"

