# Sentinel - Online Examination System

## Overview
AI-Based Cheating Pattern Detection System with comprehensive classroom and exam management features.

**Tech Stack**: Django + DRF + React + TypeScript + Tailwind CSS

## Features Implemented

### 🎨 Modern UI/UX
- **Responsive Navigation Bar**: Fixed navbar with smooth animations, role-based navigation
- **Modern Design**: Gradient backgrounds, hover effects, and smooth transitions
- **Loading States**: Beautiful loading spinners and skeleton screens
- **Responsive Layout**: Mobile-first design that works on all devices

### 🔐 Authentication & Authorization
- **Role-Based Access Control**: Three distinct roles (Admin, Teacher, Student)
- **JWT Authentication**: Secure token-based authentication
- **Protected Routes**: Route guards based on user roles
- **Automatic Redirects**: Users redirected to appropriate dashboards after login

### 🏫 Classroom Management (Teacher Features)
- **Create Classrooms**: Teachers can create classrooms with unique IDs and passwords
- **Auto-Generated IDs**: Secure, random classroom ID generation
- **Password Protection**: Classroom access controlled by passwords
- **Member Management**: View and manage students in classrooms
- **Classroom Analytics**: Track member count and exam statistics

### 📝 Exam Management (Teacher Features)
- **Create Exams**: Full exam creation with title, description, duration
- **Question Types**: Support for Multiple Choice, True/False, Short Answer, Essay
- **Bulk Question Import**: Add multiple questions at once
- **Exam Publishing**: Control when exams become available to students
- **Violation Limits**: Set custom violation thresholds per exam

### 👥 Student Features
- **Join Classrooms**: Students can join using classroom ID and password
- **View Available Exams**: See published exams from joined classrooms
- **Exam Information**: Duration, violation limits, question count
- **Exam Participation**: Take exams with real-time monitoring

### 📈 Results & Analytics (Teacher Features)
- **Real-time Results**: View student performance as they complete exams
- **Violation Tracking**: Monitor student violations during exams
- **Session Status**: Track exam completion status (Ongoing, Completed, Terminated)
- **Performance Metrics**: Total marks, violation counts, time tracking

## User Workflows

### Teacher Workflow
1. Login with teacher credentials → Redirected to Teacher Dashboard
2. Create classroom with name, password, description
3. Share classroom ID and password with students
4. Create exam with multiple question types
5. Publish exam to make it available to students
6. Monitor student progress and view results

### Student Workflow
1. Login with student credentials → Redirected to Student Dashboard
2. Join classroom using classroom ID and password
3. View available published exams from joined classrooms
4. Start exam and answer questions
5. Submit exam before time limit

## Setup Instructions

### Backend Setup
1. Navigate to project directory: `cd E:\Miniproject\project1`
2. Create virtual environment: `python -m venv venv`
3. Activate virtual environment: `venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Start Django server: `python manage.py runserver`

### Frontend Setup
1. Navigate to frontend: `cd frontend`
2. Install dependencies: `npm install`
3. Start React server: `npm start`
4. Open browser to `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /auth/login/` - User login with role-based redirect
- `POST /auth/register/` - User registration
- `GET /users/me/` - Get current user info

### Classrooms
- `GET /classrooms/` - List user's classrooms
- `POST /classrooms/` - Create new classroom
- `POST /classrooms/join_classroom/` - Join classroom with ID/password
- `GET /classrooms/{id}/results/` - Get exam results for classroom

### Exams & Questions
- `GET /exams/` - List accessible exams (filtered by role)
- `POST /exams/` - Create new exam
- `POST /exams/{id}/publish/` - Publish exam
- `GET /exams/{id}/questions/` - List exam questions
- `POST /exams/{id}/questions/` - Create question
- `POST /exams/{id}/questions/bulk/` - Bulk create questions

## Current Status

✅ **Completed**:
- Modern responsive UI with navigation bar
- Complete authentication with role-based redirects
- Classroom creation and management system
- Exam creation with multiple question types
- Student classroom joining functionality
- Results tracking and analytics
- Database models and API endpoints

🚧 **Ready for Enhancement**:
- Real-time exam proctoring
- Advanced violation detection
- Video monitoring integration
- Email notifications
- Export functionality

The system is fully functional and ready for testing!
  - python manage.py migrate
  - python manage.py createsuperuser
  - python manage.py runserver

Authentication
- POST /api/auth/login/ { username, password } -> { access, refresh, role }
- POST /api/auth/refresh/ { refresh } -> { access }

Roles
- Admin, Teacher, Student. Custom `users.User.role`.

Core Endpoints (examples)
- Users (Admin only): GET/POST/PUT/PATCH/DELETE /api/users/
- Exams: 
  - Teacher/Admin: CRUD /api/exams/
  - Student: GET published list /api/exams/
  - Questions: /api/exams/{id}/questions/
  - Start: POST /api/exams/{id}/start/
  - Submit: POST /api/exams/{id}/submit/
- Sessions: GET /api/sessions/{id}/
- Violations:
  - Log: POST /api/violations/log/
  - Report: GET /api/violations/report/?exam=1&student=2&start=...&end=...
- Admin Settings: GET/PATCH /api/admin/settings/

Example curl
```bash
curl -X POST http://localhost:8000/api/auth/login/ -H "Content-Type: application/json" -d '{"username":"student","password":"pass"}'

curl -H "Authorization: Bearer $ACCESS" http://localhost:8000/api/exams/

curl -X POST -H "Authorization: Bearer $ACCESS" http://localhost:8000/api/exams/1/start/

curl -X POST -H "Authorization: Bearer $ACCESS" -H "Content-Type: application/json" \
  -d '{"answers":[{"question":1,"mcq_choice":1},{"question":2,"short_text":"hi"}]}' \
  http://localhost:8000/api/exams/1/submit/

curl -X POST -H "Authorization: Bearer $ACCESS" -H "Content-Type: application/json" \
  -d '{"session_id":1,"violation_type":"TAB_SWITCH","timestamp":"2025-01-01T00:00:00Z","details":"switch"}' \
  http://localhost:8000/api/violations/log/
```

Real-time logging
- For near-real-time, the client posts to /api/violations/log/ as events occur. Endpoint increments `violation_count` and auto-terminates when `violation_limit` reached.
- For scale, add Redis + Celery to offload logging to async tasks and to fan-out notifications.
- WebSocket plan: Use Django Channels; broadcast termination events to a session room. Fallback polling: GET /api/sessions/{id}/ every 2–5s.

Security & Privacy
- JWT auth via SimpleJWT; strict serializers; no binary media stored.
- Rate limiting using django-ratelimit on /violations/log/.
- Store only metadata for violations; optionally add hashed IDs if needed.

Frontend (React + TS + Tailwind)
- See `frontend/` for app with routes: Login, Dashboards (Admin/Teacher/Student), ExamPage with timer and violation posting.
- Services: `services/api.ts` with axios + refresh interceptors; `sessionService.ts`, `violationService.ts`.
- Hooks: `useAuth`, `useWebSocket(sessionId)`.

