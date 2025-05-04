from django.test import TestCase
from .models import Block, Classroom

class ClassroomModelTests(TestCase):
    def setUp(self):
        self.block = Block.objects.create(name='A Block')
        self.classroom = Classroom.objects.create(name='CSE101', block=self.block)

    def test_classroom_str(self):
        self.assertEqual(str(self.classroom), 'CSE101')
