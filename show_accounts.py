#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from users.models import User

def show_accounts():
    """Display all active accounts with their passwords."""
    
    print("=" * 60)
    print("         ACTIVE ACCOUNTS WITH PASSWORDS")
    print("=" * 60)
    print()
    
    users = User.objects.filter(is_active=True).order_by('username')
    
    for user in users:
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Role: {user.role}")
        
        # Determine password based on account type
        if "@" in user.username:
            password = "password123"
        elif user.username == "admin":
            password = "admin123"
        else:
            password = f"{user.username}123"
            
        print(f"Password: {password}")
        print(f"Active: {user.is_active}")
        print(f"Date Joined: {user.date_joined.strftime('%Y-%m-%d %H:%M')}")
        print("-" * 50)
    
    print(f"\nTotal Active Accounts: {users.count()}")
    print()
    print("PASSWORD PATTERNS:")
    print("• Email-based accounts (contains @): password123")
    print("• Admin account: admin123")
    print("• Other test accounts: [username]123")

if __name__ == '__main__':
    show_accounts()