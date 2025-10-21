from django.test import TestCase
from rest_framework.test import APIClient

from users.models import User
from exams.models import Exam, Question
from sessions.models import ExamSession


class ViolationLogTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.teacher = User.objects.create_user(username='teacher', password='pass', role='TEACHER')
        self.student = User.objects.create_user(username='student', password='pass', role='STUDENT')
        self.exam = Exam.objects.create(teacher=self.teacher, title='E', duration_minutes=10, violation_limit=2, is_published=True)
        Question.objects.create(exam=self.exam, type='MCQ', text='Q', choices=['a','b'], correct_answer=0, marks=1)
        self.session = ExamSession.objects.create(exam=self.exam, student=self.student)

    def test_auto_terminate_on_limit(self):
        self.client.force_authenticate(self.student)
        payload = {
            'session_id': self.session.id,
            'violation_type': 'TAB_SWITCH',
            'timestamp': '2025-01-01T00:00:00Z',
            'details': 'test',
        }
        r1 = self.client.post('/api/violations/log/', data=payload, format='json')
        self.assertEqual(r1.status_code, 201)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'ONGOING')
        payload['timestamp'] = '2025-01-01T00:00:02Z'
        r2 = self.client.post('/api/violations/log/', data=payload, format='json')
        self.assertEqual(r2.status_code, 201)
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'TERMINATED')
from django.test import TestCase

# Create your tests here.
