from datetime import timedelta

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
# from django_ratelimit.decorators import ratelimit
# from django.utils.decorators import method_decorator
from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from users.permissions import IsAdmin
from sessions.models import ExamSession
from exams.models import Exam
from .models import Violation
from .serializers import ViolationSerializer, ViolationLogSerializer


# @method_decorator(ratelimit(key='ip', rate='10/10s', block=True), name='log_violation')
class ViolationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Violation.objects.select_related('session', 'student', 'session__exam')
    serializer_class = ViolationSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['details', 'violation_type']
    ordering_fields = ['created_at', 'timestamp']

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        role = getattr(user, 'role', None)
        if role == 'ADMIN':
            return qs
        if role == 'TEACHER':
            return qs.filter(session__exam__teacher=user)
        return qs.filter(student=user)

    @action(detail=False, methods=['post'], url_path='log', permission_classes=[permissions.IsAuthenticated])
    def log_violation(self, request):
        serializer = ViolationLogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session_id = serializer.validated_data['session_id']
        vtype = serializer.validated_data['violation_type']
        ts = serializer.validated_data['timestamp']
        details = serializer.validated_data.get('details', '')

        session = get_object_or_404(ExamSession.objects.select_related('exam', 'student'), pk=session_id)
        if session.status != ExamSession.Status.ONGOING:
            return Response({'detail': 'Session not ongoing.'}, status=status.HTTP_400_BAD_REQUEST)
        if request.user != session.student and getattr(request.user, 'role', None) not in ('TEACHER', 'ADMIN'):
            return Response({'detail': 'Not allowed to log for this session.'}, status=status.HTTP_403_FORBIDDEN)

        with transaction.atomic():
            violation = Violation.objects.create(
                session=session,
                student=session.student,
                violation_type=vtype,
                timestamp=ts,
                details=details,
            )
            session.violation_count = session.violation_count + 1
            # auto-terminate if limit reached
            limit = session.exam.violation_limit
            if session.violation_count >= limit:
                session.terminate()
            else:
                session.update_time_left()
            session.save()

        terminated = session.status == ExamSession.Status.TERMINATED
        payload = {
            'session_id': session.id,
            'violation_id': violation.id,
            'violation_count': session.violation_count,
            'terminated': terminated,
            'time_left': session.time_left,
            'status': session.status,
        }
        return Response(payload, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='report', permission_classes=[permissions.IsAuthenticated])
    def report(self, request):
        qs = self.get_queryset()
        # optional filters: date range, exam, student
        start = request.query_params.get('start')
        end = request.query_params.get('end')
        exam_id = request.query_params.get('exam')
        student_id = request.query_params.get('student')

        if start:
            qs = qs.filter(timestamp__gte=start)
        if end:
            qs = qs.filter(timestamp__lte=end)
        if exam_id:
            qs = qs.filter(session__exam_id=exam_id)
        if student_id:
            qs = qs.filter(student_id=student_id)

        page = self.paginate_queryset(qs)
        if page is not None:
            return self.get_paginated_response(ViolationSerializer(page, many=True).data)
        return Response(ViolationSerializer(qs, many=True).data)
from django.shortcuts import render

# Create your views here.
