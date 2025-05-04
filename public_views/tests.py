from django.test import TestCase

class PublicViewsTests(TestCase):
    def test_student_portal_access(self):
        response = self.client.get('/public/portal/')
        self.assertEqual(response.status_code, 200)
