# Admin Dashboard - Testing Guide

## Overview
The Admin Dashboard provides comprehensive system management capabilities including user management, exam oversight, and results analytics.

## Admin Credentials
- **Username:** `admin`
- **Password:** `admin123`

**OR**

- **Username:** `newadmin`
- **Email:** `newadmin@example.com`
- **Password:** `newadmin123`

## Features

### 1. Statistics Overview
- **Total Users:** Count of all registered users
- **Active Users:** Count of users who are not banned
- **Total Exams:** Count of all exams in the system
- **Total Sessions:** Count of all exam sessions

### 2. Users Management Tab
**Features:**
- View all users in a table with:
  - Full name and username
  - Email address
  - Role badge (Admin/Teacher/Student)
  - Status badge (Active/Banned)
  - Join date
  - Ban/Unban action button

**Filters:**
- **Role Filter:** All Roles / Admin / Teacher / Student
- **Status Filter:** All Status / Active / Banned
- **Search:** Search by name, email, or username

**Actions:**
- **Ban User:** Sets `is_active = False`, prevents login
- **Unban User:** Sets `is_active = True`, restores login access
- **Restrictions:** Cannot ban admin users, cannot ban yourself

### 3. Exams Overview Tab
**Features:**
- View all exams in a grid layout
- Each exam card shows:
  - Exam title and description
  - Teacher name
  - Duration in minutes
  - Number of questions
  - Violation limit
  - "View Results" button

**Filters:**
- **Search:** Search by exam title, description, or teacher name

**Actions:**
- **View Results:** Redirects to exam results page for that exam

### 4. Results Analytics Tab
**Features:**
- View all exam sessions in a table with:
  - Student name and username
  - Exam title
  - Score percentage (bold red)
  - Violations count (color-coded badge)
  - Start date/time
  - End date/time
  - Pass/Fail status (green for ≥50%, red for <50%)

**Filters:**
- **Search:** Search by student name or exam title

## API Endpoints

### User Management
```
GET /api/users/
- Returns list of all users
- Admin-only permission
```

```
POST /api/users/{id}/ban/
- Bans a user (sets is_active=False)
- Admin-only permission
- Cannot ban admins
- Cannot self-ban
```

```
POST /api/users/{id}/unban/
- Unbans a user (sets is_active=True)
- Admin-only permission
```

### Exams
```
GET /api/exams/
- Returns list of all exams
```

### Sessions
```
GET /api/sessions/
- Returns list of all exam sessions
```

## Testing Steps

### 1. Login as Admin
1. Navigate to http://localhost:8000/
2. Click "Login"
3. Enter admin credentials (admin / admin123)
4. Should redirect to `/admin` dashboard

### 2. Test Statistics Cards
1. Verify Total Users count matches database
2. Verify Active Users count (should be all users initially)
3. Verify Total Exams count
4. Verify Total Sessions count

### 3. Test Users Management
**View Users:**
1. Click "Users Management" tab
2. Verify all users are displayed
3. Check that each user shows correct role badge
4. Check that all users show "Active" status badge

**Filter by Role:**
1. Select "Student" from Role dropdown
2. Verify only students are shown
3. Select "Teacher" from Role dropdown
4. Verify only teachers are shown
5. Select "Admin" from Role dropdown
6. Verify only admins are shown

**Filter by Status:**
1. Select "Active" from Status dropdown
2. Verify all active users shown
3. Ban a student user
4. Select "Banned" from Status dropdown
5. Verify banned user appears

**Search:**
1. Enter "Anjali" in search box
2. Verify only matching users shown
3. Enter "gmail.com" in search box
4. Verify all users with gmail addresses shown

**Ban User:**
1. Find a student user
2. Click "Ban" button
3. Confirm the action
4. Verify status changes to "Banned" (red badge)
5. Verify button changes to "Unban"
6. Logout and try to login as banned user
7. Verify login is denied

**Unban User:**
1. Click "Unban" button on banned user
2. Verify status changes to "Active" (green badge)
3. Verify button changes to "Ban"
4. Try to login as user
5. Verify login succeeds

**Ban Restrictions:**
1. Try to ban an admin user
2. Verify no Ban button appears for admins
3. Verify you cannot ban yourself

### 4. Test Exams Overview
**View Exams:**
1. Click "Exams Overview" tab
2. Verify all exams are displayed in cards
3. Check each card shows:
   - Exam title
   - Description
   - Teacher name
   - Duration
   - Question count
   - Violation limit

**Search:**
1. Enter exam title in search box
2. Verify only matching exams shown
3. Enter teacher name in search box
4. Verify exams by that teacher shown

**View Results:**
1. Click "View Results" on an exam
2. Verify redirect to exam results page
3. Verify correct exam data is shown

### 5. Test Results Analytics
**View Results:**
1. Click "Results Analytics" tab
2. Verify all exam sessions are displayed
3. Check each session shows:
   - Student name and username
   - Exam title
   - Score percentage
   - Violations count
   - Start/end timestamps
   - Pass/Fail status

**Search:**
1. Enter student name in search box
2. Verify only matching sessions shown
3. Enter exam title in search box
4. Verify only sessions for that exam shown

**Score Display:**
1. Verify scores are displayed as percentages
2. Verify scores ≥50% show "Pass" (green badge)
3. Verify scores <50% show "Fail" (red badge)

**Violations:**
1. Verify sessions with 0 violations show green badge
2. Verify sessions with >0 violations show red badge

## Theme Verification
- Background: Red to rose gradient
- Tab selection: Red border and red background
- Buttons: Red gradient with hover effects
- Active elements: Red accents
- Tables: Red gradient headers
- Badges: Color-coded (green for success, red for warnings)

## Security Checks
1. **Login as Student:**
   - Navigate to `/admin`
   - Verify redirect to `/` (not authorized)

2. **Login as Teacher:**
   - Navigate to `/admin`
   - Verify redirect to `/` (not authorized)

3. **Without Login:**
   - Navigate to `/admin`
   - Verify redirect to `/login`

4. **Ban API:**
   - As non-admin, try POST to `/api/users/{id}/ban/`
   - Verify 403 Forbidden response

## Known Data
**Test Exam:** Sample Math Test (ID: 9)
- 4 questions
- 3 completed sessions:
  - Anjali@gmail.com: 100%
  - Pranav@gmail.com: 83.3%
  - nandhu@gmail.com: 66.7%

**Users:**
- 13 total active users
- 3 admins (admin, newadmin, and one more)
- 4 teachers
- 6 students

## Troubleshooting

### Admin Dashboard Not Loading
1. Check browser console for errors
2. Verify API endpoints are responding:
   ```
   GET http://localhost:8000/api/users/
   GET http://localhost:8000/api/exams/
   GET http://localhost:8000/api/sessions/
   ```
3. Verify JWT token is valid in localStorage

### Ban/Unban Not Working
1. Check Network tab for API response
2. Verify you're logged in as admin
3. Verify not trying to ban admin or yourself
4. Check backend logs for errors

### Filters Not Working
1. Refresh the page
2. Clear filters and reapply
3. Check browser console for JavaScript errors

### Navigation Issues
1. Verify you're logged in as admin
2. Check App.tsx routes are correctly configured
3. Verify ProtectedRoute includes ADMIN role
