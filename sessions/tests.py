from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from users.models import User
from exams.models import Exam, Question
from sessions.models import ExamSession


class SessionFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin', password='pass', role='ADMIN')
        self.teacher = User.objects.create_user(username='teacher', password='pass', role='TEACHER')
        self.student = User.objects.create_user(username='student', password='pass', role='STUDENT')

        self.exam = Exam.objects.create(
            teacher=self.teacher,
            title='Sample Exam',
            duration_minutes=30,
            violation_limit=3,
            is_published=True,
        )
        Question.objects.create(exam=self.exam, type='MCQ', text='2+2=?', choices=["3","4","5"], correct_answer=1, marks=2, order=1)
        Question.objects.create(exam=self.exam, type='SHORT_ANSWER', text='Say hi', marks=1, order=2)

    def test_student_can_start_and_submit_exam(self):
        # start exam
        self.client.force_authenticate(self.student)
        resp = self.client.post(f"/api/exams/{self.exam.id}/start/", data={})
        self.assertEqual(resp.status_code, 201)
        session_id = resp.data['id']
        self.assertEqual(resp.data['status'], 'ONGOING')
        self.assertTrue(resp.data['time_left'] > 0)

        # submit exam with answers
        answers = [
            {"question": self.exam.questions.first().id, "mcq_choice": 1},
            {"question": self.exam.questions.last().id, "short_text": "hi"},
        ]
        resp2 = self.client.post(f"/api/exams/{self.exam.id}/submit/", data={"answers": answers}, format='json')
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.data['status'], 'COMPLETED')
        self.assertGreaterEqual(resp2.data['total_marks'], 2.0)
from django.test import TestCase

# Create your tests here.
