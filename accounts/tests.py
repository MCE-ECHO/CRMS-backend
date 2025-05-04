from django.test import TestCase
from django.contrib.auth.models import User
from .models import TeacherProfile, StudentProfile, Event

class AccountsModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.teacher = User.objects.create_user(username='teacher', password='12345', is_staff=True)

    def test_teacher_profile_creation(self):
        profile = TeacherProfile.objects.get(user=self.teacher)
        self.assertTrue(hasattr(self.teacher, 'teacherprofile'))

    def test_student_profile_creation(self):
        profile = StudentProfile.objects.get(user=self.user)
        self.assertEqual(str(profile), 'testuser')

    def test_event_creation(self):
        event = Event.objects.create(
            title='Test Event',
            start_date='2025-05-05T10:00:00',
            end_date='2025-05-05T12:00:00',
            visibility='public',
            created_by=self.user
        )
        self.assertEqual(str(event), 'Test Event')
