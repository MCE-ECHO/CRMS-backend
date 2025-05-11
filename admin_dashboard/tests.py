from django.test import TestCase
from django.contrib.auth.models import User

class AdminDashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username='admin', password='12345', email='admin@example.com')

    def test_admin_dashboard_access(self):
        self.client.login(username='admin', password='12345')
        response = self.client.get('/admin-dashboard/')
        self.assertEqual(response.status_code, 200)
