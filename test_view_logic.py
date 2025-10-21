#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from exams.models import Exam
from sessions.models import ExamSession
from django.db.models import Sum

def test_exam_results_logic():
    """Test the exact logic from the exam_results view"""
    
    teacher = User.objects.filter(role='TEACHER').first()
    if not teacher:
        print("No teacher found!")
        return
    
    exam = Exam.objects.filter(teacher=teacher, title="Sample Math Test").first()
    if not exam:
        print("No exam found!")
        return
    
    print(f"Testing exam: {exam.title} (ID: {exam.id})")
    print()
    
    # Get all completed sessions for this exam
    sessions = ExamSession.objects.filter(
        exam=exam,
        status=ExamSession.Status.COMPLETED
    ).select_related('student').prefetch_related('violations').order_by('-ended_at')
    
    print(f"Found {sessions.count()} completed sessions")
    print()
    
    # Build response data (same as view)
    results = []
    for session in sessions:
        try:
            violation_count = session.violations.count()
            score = session.score
            percentage = round((score / session.total_marks * 100) if session.total_marks > 0 else 0, 2)
            time_taken = str(session.ended_at - session.started_at) if session.ended_at else None
            
            result = {
                'session_id': session.id,
                'student_name': f"{session.student.first_name} {session.student.last_name}",
                'student_username': session.student.username,
                'student_email': session.student.email,
                'score': score,
                'total_marks': session.total_marks,
                'percentage': percentage,
                'violations_count': violation_count,
                'started_at': session.started_at,
                'completed_at': session.ended_at,
                'time_taken': time_taken,
            }
            results.append(result)
            print(f"✓ Session {session.id} - {session.student.username}: {score}/{session.total_marks} ({percentage}%)")
        except Exception as e:
            print(f"✗ ERROR processing session {session.id}: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print(f"Successfully processed {len(results)} results")
    print()
    print("Response data:")
    response = {
        'exam_title': exam.title,
        'exam_id': exam.id,
        'total_students': len(results),
        'results': results
    }
    
    import json
    print(json.dumps(response, indent=2, default=str))

if __name__ == '__main__':
    test_exam_results_logic()
