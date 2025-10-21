#!/usr/bin/env python
import os
import django
from datetime import timedelta
from django.utils import timezone

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from exams.models import Exam, Question
from sessions.models import ExamSession, Answer
from violations.models import Violation

def create_test_exam_sessions():
    """Create test exam sessions with results"""
    
    # Get teacher and students
    teacher = User.objects.filter(role='TEACHER').first()
    students = User.objects.filter(role='STUDENT')[:3]  # Get 3 students
    
    if not teacher:
        print("No teacher found!")
        return
    
    if students.count() == 0:
        print("No students found!")
        return
    
    # Get or create an exam
    exam = Exam.objects.filter(teacher=teacher, is_published=True).first()
    
    if not exam:
        print("Creating test exam...")
        exam = Exam.objects.create(
            teacher=teacher,
            title="Sample Math Test",
            description="Test exam with sample questions",
            duration_minutes=60,
            violation_limit=3,
            is_published=True,
            password="test123"
        )
        
        # Add some questions
        questions_data = [
            {
                'text': 'What is 2 + 2?',
                'type': 'MCQ',
                'choices': ['3', '4', '5', '6'],
                'correct_answer': '1',
                'marks': 2
            },
            {
                'text': 'What is 10 - 5?',
                'type': 'MCQ',
                'choices': ['3', '4', '5', '6'],
                'correct_answer': '2',
                'marks': 2
            },
            {
                'text': 'The Earth is flat.',
                'type': 'TRUE_FALSE',
                'correct_answer': '1',  # False
                'marks': 1
            },
            {
                'text': 'Python is a programming language.',
                'type': 'TRUE_FALSE',
                'correct_answer': '0',  # True
                'marks': 1
            }
        ]
        
        for idx, q_data in enumerate(questions_data):
            Question.objects.create(
                exam=exam,
                text=q_data['text'],
                type=q_data['type'],
                choices=q_data.get('choices'),
                correct_answer=q_data['correct_answer'],
                marks=q_data['marks'],
                order=idx
            )
        
        print(f"Created exam: {exam.title} with {len(questions_data)} questions")
    
    # Get questions
    questions = list(exam.questions.all())
    total_marks = sum(q.marks for q in questions)
    
    print(f"\nUsing exam: {exam.title} (ID: {exam.id})")
    print(f"Total questions: {len(questions)}")
    print(f"Total marks: {total_marks}")
    print()
    
    # Create sessions for students with different outcomes
    scenarios = [
        {'student_idx': 0, 'correct_answers': 4, 'violations': 0, 'name': 'Perfect Score'},
        {'student_idx': 1, 'correct_answers': 3, 'violations': 1, 'name': 'Good Score with 1 violation'},
        {'student_idx': 2, 'correct_answers': 2, 'violations': 2, 'name': 'Average Score with 2 violations'},
    ]
    
    for scenario in scenarios:
        if scenario['student_idx'] >= students.count():
            continue
            
        student = students[scenario['student_idx']]
        
        # Check if session already exists
        existing = ExamSession.objects.filter(exam=exam, student=student).first()
        if existing:
            print(f"Session already exists for {student.username} - deleting old one")
            existing.delete()
        
        # Create session
        now = timezone.now()
        started_at = now - timedelta(hours=1)
        ended_at = started_at + timedelta(minutes=45)
        
        session = ExamSession(
            exam=exam,
            student=student,
            status='COMPLETED',
            total_marks=total_marks
        )
        # Override auto_now_add for started_at
        session.started_at = started_at
        session.ended_at = ended_at
        session.save()
        
        # Add answers
        correct_count = 0
        score = 0
        for idx, question in enumerate(questions):
            # First N answers are correct based on scenario
            is_correct = idx < scenario['correct_answers']
            
            # For MCQ, correct_answer is the index as string
            if question.type == 'MCQ':
                correct_choice = int(question.correct_answer)
                mcq_choice = correct_choice if is_correct else (correct_choice + 1) % len(question.choices)
                marks = question.marks if is_correct else 0.0
                
                Answer.objects.create(
                    session=session,
                    question=question,
                    mcq_choice=mcq_choice,
                    marks_awarded=marks
                )
            else:  # TRUE_FALSE
                correct_choice = int(question.correct_answer)
                mcq_choice = correct_choice if is_correct else (1 - correct_choice)
                marks = question.marks if is_correct else 0.0
                
                Answer.objects.create(
                    session=session,
                    question=question,
                    mcq_choice=mcq_choice,
                    marks_awarded=marks
                )
            
            if is_correct:
                correct_count += 1
                score += question.marks
        
        # Add violations
        violation_types = ['MULTIPLE_FACES', 'LOOKING_AWAY', 'TAB_SWITCH']
        for v_idx in range(scenario['violations']):
            violation_time = started_at + timedelta(minutes=10 * (v_idx + 1))
            Violation.objects.create(
                session=session,
                student=student,
                violation_type=violation_types[v_idx % len(violation_types)],
                timestamp=violation_time,
                details=f"Test violation {v_idx + 1}"
            )
        
        percentage = (score / total_marks * 100) if total_marks > 0 else 0
        status_text = "PASS" if percentage >= 50 else "FAIL"
        
        print(f"✓ Created session for {student.username}:")
        print(f"  - Scenario: {scenario['name']}")
        print(f"  - Score: {score}/{total_marks} ({percentage:.1f}%) - {status_text}")
        print(f"  - Violations: {scenario['violations']}")
        print(f"  - Time taken: 45 minutes")
        print()
    
    print("="*60)
    print("SUCCESS! Test sessions created.")
    print("="*60)
    print(f"\nNow you can view results at:")
    print(f"  Teacher Dashboard → Exam '{exam.title}' → Results button")
    print(f"  Or navigate to: http://localhost:3000/teacher/exam-results/{exam.id}")
    print()

if __name__ == '__main__':
    create_test_exam_sessions()
