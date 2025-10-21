#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from exams.models import Exam
from sessions.models import ExamSession

def test_score_property():
    """Test if the score property works"""
    
    teacher = User.objects.filter(role='TEACHER').first()
    if not teacher:
        print("No teacher found!")
        return
    
    exam = Exam.objects.filter(teacher=teacher, title="Sample Math Test").first()
    if not exam:
        print("Sample Math Test not found!")
        return
    
    sessions = ExamSession.objects.filter(exam=exam, status='COMPLETED')
    
    print(f"Testing score property for {sessions.count()} sessions:")
    print()
    
    for session in sessions:
        try:
            score = session.score
            print(f"✓ Session {session.id} ({session.student.username}): score = {score}")
        except Exception as e:
            print(f"✗ Session {session.id} ({session.student.username}): ERROR - {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    test_score_property()
