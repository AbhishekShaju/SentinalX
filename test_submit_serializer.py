#!/usr/bin/env python
"""Test the submit serializer with sample data"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from sessions.serializers import SubmitExamSerializer

# Sample payload that frontend would send
sample_payload = {
    'answers': [
        {'question_id': 1, 'mcq_choice': 0},
        {'question_id': 2, 'short_text': 'Sample answer'},
        {'question_id': 3, 'mcq_choice': 2},
    ]
}

print("Testing SubmitExamSerializer with sample payload:")
print(f"Payload: {sample_payload}")

# Test without context first (should work for data validation)
from sessions.models import ExamSession
from exams.models import Exam
from django.contrib.auth import get_user_model

User = get_user_model()

# Create a mock session for context
try:
    user = User.objects.filter(role='STUDENT').first()
    exam = Exam.objects.first()
    if user and exam:
        session = ExamSession.objects.filter(student=user, exam=exam).first()
        if not session:
            print("⚠️ No session found, testing validation only")
            session = None
    else:
        print("⚠️ No user/exam found, testing validation only")
        session = None
except Exception as e:
    print(f"⚠️ Could not create test session: {e}")
    session = None

# Create a dummy session object for testing
class DummySession:
    class Status:
        ONGOING = 'ONGOING'
        TERMINATED = 'TERMINATED'
    status = Status.ONGOING

if not session:
    session = DummySession()

context = {'session': session}
serializer = SubmitExamSerializer(data=sample_payload, context=context)
if serializer.is_valid():
    print("✅ Serializer is valid!")
    print(f"Validated data: {serializer.validated_data}")
else:
    print("❌ Serializer validation failed!")
    print(f"Errors: {serializer.errors}")
