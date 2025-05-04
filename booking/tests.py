from django.test import TestCase
from django.contrib.auth.models import User
from .models import Booking
from classroom.models import Classroom, Block

class BookingModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.block = Block.objects.create(name='A Block')
        self.classroom = Classroom.objects.create(name='CSE101', block=self.block)

    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            classroom=self.classroom,
            date='2025-05-05',
            start_time='10:00',
            end_time='11:00',
            status='pending'
        )
        self.assertEqual(str(booking), 'CSE101 - 2025-05-05 10:00:00-11:00:00')
