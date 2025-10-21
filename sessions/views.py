from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

from exams.models import Exam
from .models import ExamSession
from .serializers import ExamSessionSerializer, ExamSessionSummarySerializer, StartExamSerializer, SubmitExamSerializer
from .pdf_generator import generate_exam_result_pdf
from django_ratelimit.decorators import ratelimit



class ExamSessionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ExamSession.objects.select_related('exam', 'student').prefetch_related('answers__question')
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ExamSessionSerializer
        return ExamSessionSummarySerializer

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        role = getattr(user, 'role', None)
        if role == 'ADMIN':
            return qs
        if role == 'TEACHER':
            return qs.filter(exam__teacher=user)
        return qs.filter(student=user)

    @action(detail=False, methods=['post'], url_path=r'exams/(?P<exam_id>[^/.]+)/start')
    def start_exam(self, request, exam_id=None):
        user = request.user
        if getattr(user, 'role', None) != 'STUDENT':
            return Response({'detail': 'Only students can start exams.'}, status=status.HTTP_403_FORBIDDEN)
        exam = get_object_or_404(Exam, pk=exam_id, is_published=True)
        
        # Check if student already has a completed session for this exam
        existing_completed = ExamSession.objects.filter(
            exam=exam,
            student=user,
            status=ExamSession.Status.COMPLETED
        ).exists()
        
        if existing_completed:
            return Response(
                {'detail': 'You have already completed this exam. Only one attempt is allowed per exam.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if student already has an ongoing or terminated session
        existing_active = ExamSession.objects.filter(
            exam=exam,
            student=user,
            status__in=[ExamSession.Status.ONGOING, ExamSession.Status.TERMINATED]
        ).order_by('-started_at').first()
        
        if existing_active:
            # Return the existing session instead of creating a new one
            return Response(ExamSessionSerializer(existing_active).data, status=status.HTTP_200_OK)
        
        # Create new session
        serializer = StartExamSerializer(data=request.data, context={'request': request, 'exam': exam})
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response(ExamSessionSerializer(session).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path=r'exams/(?P<exam_id>[^/.]+)/submit')
    def submit_exam(self, request, exam_id=None):
        user = request.user
        if getattr(user, 'role', None) != 'STUDENT':
            return Response({'detail': 'Only students can submit exams.'}, status=status.HTTP_403_FORBIDDEN)
        exam = get_object_or_404(Exam, pk=exam_id)
        
        # Get the most recent session that is ONGOING or TERMINATED (not COMPLETED)
        # Order by started_at descending to get the latest session
        try:
            session = ExamSession.objects.filter(
                exam=exam, 
                student=user, 
                status__in=[ExamSession.Status.ONGOING, ExamSession.Status.TERMINATED]
            ).order_by('-started_at').first()
            
            if not session:
                return Response(
                    {'detail': 'No active or terminated session found for this exam.'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        except ExamSession.DoesNotExist:
            return Response(
                {'detail': 'No active session found for this exam.'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SubmitExamSerializer(data=request.data, context={'session': session})
        serializer.is_valid(raise_exception=True)
        session = serializer.save()
        return Response(ExamSessionSerializer(session).data)

    @action(detail=False, methods=['get'], url_path=r'exams/(?P<exam_id>[^/.]+)/results')
    def exam_results(self, request, exam_id=None):
        """Get all student results for a specific exam (Teacher only)"""
        user = request.user
        role = getattr(user, 'role', None)
        
        # Only teachers and admins can view exam results
        if role not in ['TEACHER', 'ADMIN']:
            return Response(
                {'detail': 'Only teachers can view exam results.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get the exam
        exam = get_object_or_404(Exam, id=exam_id)
        
        # Check if teacher owns this exam (admins can view all)
        if role == 'TEACHER' and exam.teacher != user:
            return Response(
                {'detail': 'You can only view results for your own exams.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get all completed sessions for this exam
        sessions = ExamSession.objects.filter(
            exam=exam,
            status=ExamSession.Status.COMPLETED
        ).select_related('student').prefetch_related('violations').order_by('-ended_at')
        
        # Build response data
        results = []
        for session in sessions:
            violation_count = session.violations.count()
            results.append({
                'session_id': session.id,
                'student_name': f"{session.student.first_name} {session.student.last_name}",
                'student_username': session.student.username,
                'student_email': session.student.email,
                'score': session.score,
                'total_marks': session.total_marks,
                'percentage': round((session.score / session.total_marks * 100) if session.total_marks > 0 else 0, 2),
                'violations_count': violation_count,
                'started_at': session.started_at,
                'completed_at': session.ended_at,
                'time_taken': str(session.ended_at - session.started_at) if session.ended_at else None,
            })
        
        return Response({
            'exam_title': exam.title,
            'exam_id': exam.id,
            'total_students': len(results),
            'results': results
        })

    @action(detail=True, methods=['get'], url_path='download-pdf')
    def download_pdf(self, request, pk=None):
        """Generate and download exam result as PDF"""
        session = self.get_object()
        
        # Check if user is authorized to view this session's results
        user = request.user
        role = getattr(user, 'role', None)
        
        if role == 'STUDENT' and session.student != user:
            return Response(
                {'detail': 'You can only download your own exam results.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Session must be completed to generate PDF
        if session.status not in [ExamSession.Status.COMPLETED, ExamSession.Status.TERMINATED]:
            return Response(
                {'detail': 'PDF can only be generated for completed exams.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Generate PDF
            pdf_buffer = generate_exam_result_pdf(session)
            
            # Create HTTP response with PDF
            response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
            filename = f"exam_result_{session.exam.title.replace(' ', '_')}_{session.student.username}_{session.id}.pdf"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        except Exception as e:
            return Response(
                {'detail': f'Error generating PDF: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
from django.shortcuts import render

# Create your views here.
