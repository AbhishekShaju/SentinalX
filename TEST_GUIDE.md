# Sentinals - Test Accounts & User Guide

## 🔑 Test Accounts

### Default Password Pattern:
- **Email-based accounts**: `password123`
- **Admin account**: `admin123`
- **Other test accounts**: `[username]123`

### Available Test Accounts:

#### Teacher Accounts:
```
Email: abhishek@gmail.com
Password: password123
Role: Teacher
```

#### Student Accounts:
```
Email: Anjali@gmail.com
Password: password123
Role: Student

Email: Pranav@gmail.com
Password: password123
Role: Student

Email: nandhu@gmail.com
Password: password123
Role: Student
```

#### Admin Account:
```
Username: admin
Password: admin123
Role: Admin
```

---

## 📊 Testing Exam Results Feature

### What Has Been Fixed:
1. ✅ Added `score` property to ExamSession model (calculates from answers)
2. ✅ Fixed field name from `completed_at` to `ended_at` in API
3. ✅ Created test exam "Sample Math Test" with 4 questions (6 marks total)
4. ✅ Created 3 completed exam sessions with different results:
   - **Anjali**: 6/6 (100%) - 0 violations - PASS
   - **Pranav**: 5/6 (83.3%) - 1 violation - PASS
   - **nandhu**: 4/6 (66.7%) - 2 violations - PASS

### How to Test:

#### Step 1: Start Backend Server
```bash
python manage.py runserver
```
Server will run at: http://127.0.0.1:8000/

#### Step 2: Start Frontend (Development)
```bash
cd frontend
npm start
```
Frontend will run at: http://localhost:3000/

**OR use the production build already created:**
```bash
# Just access through Django at http://127.0.0.1:8000/
```

#### Step 3: Login as Teacher
1. Go to: http://localhost:3000/login
2. Login with:
   - Email: `abhishek@gmail.com`
   - Password: `password123`

#### Step 4: View Exam Results
1. You'll see "Sample Math Test" exam in your Teacher Dashboard
2. Click the **"Results"** button on the exam card
3. You should see a table with all 3 students' results showing:
   - Student name and email
   - Score (marks/total)
   - Grade (A+, A, B, etc.)
   - **Status (PASS/FAIL)** - NEW COLUMN!
   - Violations count
   - Time taken
   - Completed timestamp
   - Download PDF button

#### Step 5: Test Student View
1. Logout and login as a student (e.g., Anjali@gmail.com)
2. Go to Student Dashboard
3. For "Sample Math Test", you should see **"View Result"** button (not "Start Exam")
4. Click it to see your detailed results

---

## 🎨 Theme Updates Completed

### Pages Updated with Red/White Theme:
- ✅ Landing Page (with animations, 9 features, demo card)
- ✅ Navbar (Sentinals branding)
- ✅ Login Page
- ✅ Register Page
- ✅ Footer
- ✅ Student Dashboard
- ✅ Teacher Dashboard
- ✅ Exam Results View (NEW - Pass/Fail column added!)

### Design Features:
- **Primary Color**: Red (#DC2626 to #F43F5E gradients)
- **Backgrounds**: from-red-50 via-white to-rose-50
- **Hover Effects**: scale-105 transforms, shadow-lg
- **Focus Rings**: red ring-500
- **Animations**: fade-in, slide-in, blob, pulse-slow

---

## 🐛 Bug Fixes Summary

### Issue: "Failed to load exam results"

**Root Causes Found:**
1. ❌ ExamSession model had no `score` field - it was being used in views but didn't exist
2. ❌ Views used `completed_at` but model has `ended_at` field
3. ❌ No test data existed - all exams had 0 completed sessions

**Fixes Applied:**
1. ✅ Added `@property score()` to ExamSession model that calculates from Answer.marks_awarded
2. ✅ Changed `completed_at` → `ended_at` in views.py response
3. ✅ Created `create_test_sessions.py` script to generate sample data
4. ✅ Added Pass/Fail status column to results table
5. ✅ Applied red/white theme to exam results page

---

## 🚀 API Endpoints Working

### Exam Results Endpoint:
```
GET /sessions/exams/{exam_id}/results/
Authentication: Required (Teacher/Admin only)
```

**Response Structure:**
```json
{
  "exam_title": "Sample Math Test",
  "exam_id": 9,
  "total_students": 3,
  "results": [
    {
      "session_id": 22,
      "student_name": "Anjali Gmail",
      "student_username": "Anjali@gmail.com",
      "student_email": "Anjali@gmail.com",
      "score": 6.0,
      "total_marks": 6.0,
      "percentage": 100.0,
      "violations_count": 0,
      "started_at": "2025-10-22T00:14:29.123Z",
      "completed_at": "2025-10-22T00:59:29.123Z",
      "time_taken": "0:45:00"
    }
  ]
}
```

---

## 📝 Quick Commands

### View All Accounts:
```bash
python show_accounts.py
```

### Create More Test Sessions:
```bash
python create_test_sessions.py
```

### Run Django Server:
```bash
python manage.py runserver
```

### Build Frontend:
```bash
cd frontend
npm run build
```

### Start Frontend Dev Server:
```bash
cd frontend
npm start
```

---

## ✨ Features Working

1. ✅ Teacher can create exams with questions (MCQ and True/False)
2. ✅ Students can take exams with AI proctoring
3. ✅ One-attempt policy enforced (can't retake after submission)
4. ✅ Teacher can view all student results with:
   - Scores and percentages
   - Grades (A+, A, B, C, F)
   - **Pass/Fail status** (50% passing grade)
   - Violation counts
   - Time taken
   - PDF download for each student
5. ✅ Students can view their own results after completion
6. ✅ Consistent red/white theme across all pages

---

## 🎯 Next Steps (Optional Enhancements)

- Add statistics dashboard for teachers (avg score, pass rate, etc.)
- Export all results to Excel/CSV
- Filter results by pass/fail, score range, violations
- Add email notifications when exam is completed
- Add detailed violation breakdown in results
- Allow teachers to adjust passing grade percentage
- Add question-wise analysis showing which questions were hardest

---

**Last Updated:** October 22, 2025  
**Status:** ✅ All features working, theme applied, test data created
