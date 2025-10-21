#!/usr/bin/env python
"""
Simple script to create test users for the examination system.
Run this after starting the Django server to create sample users.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

def create_test_users():
    """Create test users if they don't exist."""
    
    # Create admin user
    if not User.objects.filter(username='admin').exists():
        admin = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='admin123',
            role=User.Role.ADMIN,
            first_name='Admin',
            last_name='User'
        )
        print(f"✅ Created admin user: {admin.username}")
    else:
        print("ℹ️  Admin user already exists")

    # Create teacher user
    if not User.objects.filter(username='teacher').exists():
        teacher = User.objects.create_user(
            username='teacher',
            email='teacher@example.com',
            password='teacher123',
            role=User.Role.TEACHER,
            first_name='Teacher',
            last_name='User'
        )
        print(f"✅ Created teacher user: {teacher.username}")
    else:
        print("ℹ️  Teacher user already exists")

    # Create student user
    if not User.objects.filter(username='student').exists():
        student = User.objects.create_user(
            username='student',
            email='student@example.com',
            password='student123',
            role=User.Role.STUDENT,
            first_name='Student',
            last_name='User'
        )
        print(f"✅ Created student user: {student.username}")
    else:
        print("ℹ️  Student user already exists")

    print("\n🎯 Test Credentials:")
    print("Admin    - username: admin    | password: admin123")
    print("Teacher  - username: teacher  | password: teacher123")
    print("Student  - username: student  | password: student123")
    print("\nNow you can test the login flow! 🚀")

if __name__ == '__main__':
    create_test_users()