#!/usr/bin/env python
"""Test PDF generation for exam results"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from sessions.models import ExamSession
from sessions.pdf_generator import generate_exam_result_pdf

# Get a completed session
session = ExamSession.objects.filter(status='COMPLETED').first()

if not session:
    print("❌ No completed sessions found in the database.")
    print("Please complete an exam first to test PDF generation.")
else:
    print(f"✅ Found completed session: {session.id}")
    print(f"   Student: {session.student.username}")
    print(f"   Exam: {session.exam.title}")
    print(f"   Score: {session.total_marks}")
    print(f"   Status: {session.status}")
    print("\nGenerating PDF...")
    
    try:
        pdf_buffer = generate_exam_result_pdf(session)
        
        # Save to file for testing
        filename = f"test_result_{session.id}.pdf"
        with open(filename, 'wb') as f:
            f.write(pdf_buffer.read())
        
        print(f"✅ PDF generated successfully: {filename}")
        print(f"   File size: {os.path.getsize(filename)} bytes")
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()
