#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.contrib.auth import get_user_model
from exams.models import Classroom, Exam, Question

User = get_user_model()

def create_test_data():
    print("Creating test data...")
    
    # Get or create a teacher
    teacher, created = User.objects.get_or_create(
        username='teacher1',
        defaults={
            'email': 'teacher1@example.com',
            'first_name': 'John',
            'last_name': 'Teacher',
            'role': 'TEACHER'
        }
    )
    if created:
        teacher.set_password('teacher123')
        teacher.save()
        print(f"Created teacher: {teacher.username}")
    else:
        print(f"Teacher already exists: {teacher.username}")
    
    # Create a test classroom
    classroom, created = Classroom.objects.get_or_create(
        classroom_id='MATH101',
        defaults={
            'name': 'Mathematics 101',
            'description': 'Basic Mathematics Course',
            'password': 'math123',
            'teacher': teacher,
            'is_active': True
        }
    )
    
    if created:
        print(f"Created classroom: {classroom.name} (ID: {classroom.classroom_id})")
    else:
        print(f"Classroom already exists: {classroom.name} (ID: {classroom.classroom_id})")
    
    # Create a test exam
    exam, created = Exam.objects.get_or_create(
        title='Math Quiz - Score Demo',
        defaults={
            'description': 'A sample math quiz to test the score display functionality',
            'classroom': classroom,
            'teacher': teacher,
            'duration_minutes': 30,
            'violation_limit': 3,
            'is_published': True
        }
    )
    
    if created:
        print(f"Created exam: {exam.title}")
        
        # Create sample questions with correct answers
        questions_data = [
            {
                'text': 'What is 5 + 3?',
                'type': 'MCQ',
                'choices': ['6', '7', '8', '9'],
                'correct_answer': 2,  # Index 2 = '8'
                'marks': 1
            },
            {
                'text': 'What is 10 - 4?',
                'type': 'MCQ',
                'choices': ['5', '6', '7', '8'],
                'correct_answer': 1,  # Index 1 = '6'
                'marks': 1
            },
            {
                'text': 'What is 3 × 4?',
                'type': 'MCQ',
                'choices': ['10', '11', '12', '13'],
                'correct_answer': 2,  # Index 2 = '12'
                'marks': 1
            },
            {
                'text': 'What is 15 ÷ 3?',
                'type': 'MCQ',
                'choices': ['3', '4', '5', '6'],
                'correct_answer': 2,  # Index 2 = '5'
                'marks': 1
            },
            {
                'text': 'Explain how you solve 2x + 5 = 15',
                'type': 'SA',
                'choices': [],
                'correct_answer': None,
                'marks': 2
            }
        ]
        
        for i, q_data in enumerate(questions_data):
            question, created = Question.objects.get_or_create(
                exam=exam,
                text=q_data['text'],
                defaults={
                    'type': q_data['type'],
                    'choices': q_data['choices'],
                    'correct_answer': q_data['correct_answer'],
                    'marks': q_data['marks'],
                    'order': i + 1
                }
            )
            if created:
                print(f"Created question: {question.text}")
    else:
        print(f"Exam already exists: {exam.title}")
    
    print("\nTest data creation completed!")
    print("\nHow to test:")
    print("1. Login as a student (student1/student123)")
    print("2. Join classroom with ID: MATH101, Password: math123")
    print("3. Start the exam: Math Quiz - Score Demo")
    print("4. Answer questions and submit to see the score modal")
    print("\nNote: MCQ questions have correct answers set for automatic scoring")

if __name__ == '__main__':
    create_test_data()