from django.test import TestCase
from django.contrib.auth.models import User
from .models import Timetable
from classroom.models import Classroom, Block

class TimetableModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teacher', password='12345', is_staff=True)
        self.block = Block.objects.create(name='A Block')
        self.classroom = Classroom.objects.create(name='CSE101', block=self.block)
        self.timetable = Timetable.objects.create(
            classroom=self.classroom,
            teacher=self.user,
            day='Monday',
            start_time='10:00',
            end_time='11:00',
            subject_name='Math'
        )

    def test_timetable_str(self):
        self.assertEqual(str(self.timetable), 'CSE101 - Monday 10:00:00-11:00:00')
