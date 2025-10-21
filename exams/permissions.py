from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return getattr(user, 'role', None) in ('ADMIN', 'TEACHER')


class ExamReadPermission(BasePermission):
    """Students can list only published exams; teachers/admins have full access."""

    def has_permission(self, request, view):
        # Allow listing; filtering handled in view
        if request.method in SAFE_METHODS:
            return True
        # Non-read methods require admin/teacher
        user = request.user
        return bool(user and user.is_authenticated and getattr(user, 'role', None) in ('ADMIN', 'TEACHER'))

