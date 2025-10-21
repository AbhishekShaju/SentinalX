#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User
from exams.models import Classroom, Exam, ClassroomMembership

def debug_student_exam_visibility():
    print("=" * 60)
    print("         DEBUG: STUDENT EXAM VISIBILITY")
    print("=" * 60)
    
    # Get student user
    try:
        student = User.objects.get(username='student')
        print(f"✅ Found student: {student.username} (ID: {student.id})")
    except User.DoesNotExist:
        print("❌ Student user not found!")
        return
    
    print("\n" + "=" * 40)
    print("STUDENT CLASSROOM MEMBERSHIPS:")
    print("=" * 40)
    
    memberships = ClassroomMembership.objects.filter(student=student, is_active=True)
    
    if not memberships:
        print("❌ Student is not a member of any classrooms!")
        return
    
    for membership in memberships:
        classroom = membership.classroom
        print(f"✅ Member of: {classroom.name} (ID: {classroom.id})")
        print(f"   Teacher: {classroom.teacher.username}")
        print(f"   Active: {classroom.is_active}")
        print()
    
    print("=" * 40)
    print("EXAMS IN STUDENT'S CLASSROOMS:")
    print("=" * 40)
    
    student_classroom_ids = [m.classroom.id for m in memberships]
    all_exams_in_classrooms = Exam.objects.filter(classroom__in=student_classroom_ids)
    
    if not all_exams_in_classrooms:
        print("❌ No exams found in student's classrooms!")
        return
    
    for exam in all_exams_in_classrooms:
        print(f"Exam ID {exam.id}: {exam.title}")
        print(f"   Classroom: {exam.classroom.name if exam.classroom else 'No classroom'}")
        print(f"   Teacher: {exam.teacher.username}")
        print(f"   Published: {exam.is_published}")
        print(f"   Questions: {exam.questions.count()}")
        print()
    
    print("=" * 40)
    print("PUBLISHED EXAMS STUDENT SHOULD SEE:")
    print("=" * 40)
    
    published_exams = all_exams_in_classrooms.filter(is_published=True)
    
    if not published_exams:
        print("❌ No published exams in student's classrooms!")
        print("   This is why the student can't see any exams.")
    else:
        for exam in published_exams:
            print(f"✅ {exam.title} (ID: {exam.id}) in {exam.classroom.name}")
    
    print("\n" + "=" * 40)
    print("RECOMMENDATIONS:")
    print("=" * 40)
    
    if not memberships:
        print("1. Student needs to join a classroom first")
    elif not all_exams_in_classrooms:
        print("1. Teachers need to create exams in the classrooms")
    elif not published_exams:
        print("1. Teachers need to PUBLISH their exams")
        print("2. Unpublished exams are not visible to students")
    else:
        print("✅ Everything looks good! Student should see the exams.")

if __name__ == '__main__':
    debug_student_exam_visibility()