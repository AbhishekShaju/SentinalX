#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from exams.models import Exam
from sessions.models import ExamSession
import requests

def test_exam_results():
    """Test the exam results API endpoint"""
    
    # Get a teacher user
    teacher = User.objects.filter(role='TEACHER').first()
    if not teacher:
        print("No teacher found in database!")
        return
    
    print(f"Testing with teacher: {teacher.username}")
    
    # Get an exam owned by this teacher
    exam = Exam.objects.filter(teacher=teacher).first()
    if not exam:
        print(f"No exam found for teacher {teacher.username}")
        return
    
    print(f"Testing with exam: {exam.title} (ID: {exam.id})")
    
    # Check if there are any completed sessions
    completed_sessions = ExamSession.objects.filter(
        exam=exam,
        status='COMPLETED'
    ).count()
    
    print(f"Completed sessions for this exam: {completed_sessions}")
    
    # List all sessions
    all_sessions = ExamSession.objects.filter(exam=exam)
    print(f"\nAll sessions for exam {exam.id}:")
    for session in all_sessions:
        print(f"  - Session {session.id}: Student={session.student.username}, Status={session.status}, Score={session.score}/{session.total_marks}")
    
    print("\n" + "="*60)
    print("ENDPOINT INFO:")
    print("="*60)
    print(f"URL Pattern: /sessions/exams/{exam.id}/results/")
    print(f"Full URL: http://127.0.0.1:8000/sessions/exams/{exam.id}/results/")
    print(f"Method: GET")
    print(f"Auth Required: Yes (Teacher/Admin only)")
    print("\nTo test manually, use:")
    print(f"  curl -H 'Authorization: Bearer <token>' http://127.0.0.1:8000/sessions/exams/{exam.id}/results/")

if __name__ == '__main__':
    test_exam_results()
