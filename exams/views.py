from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils.timezone import now
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Exam, Question, AdminSettings, Classroom, ClassroomMembership
from .serializers import (
    ExamSerializer, QuestionSerializer, AdminSettingsSerializer,
    ClassroomSerializer, ClassroomMembershipSerializer
)
from .permissions import IsAdminOrTeacher, ExamReadPermission
from users.permissions import IsAdmin

User = get_user_model()


class ClassroomViewSet(viewsets.ModelViewSet):
    serializer_class = ClassroomSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'classroom_id']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'role') and user.role == 'TEACHER':
            return Classroom.objects.filter(teacher=user)
        elif hasattr(user, 'role') and user.role == 'ADMIN':
            return Classroom.objects.all()
        else:
            # Students can see classrooms they are members of
            return Classroom.objects.filter(memberships__student=user, memberships__is_active=True)

    def get_permissions(self):
        if self.action in ['join_classroom', 'list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [IsAdminOrTeacher()]

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def join_classroom(self, request):
        """Allow students to join a classroom with ID and password."""
        classroom_id = request.data.get('classroom_id')
        password = request.data.get('password')
        
        if not classroom_id or not password:
            return Response(
                {'error': 'Both classroom_id and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            classroom = Classroom.objects.get(classroom_id=classroom_id, is_active=True)
        except Classroom.DoesNotExist:
            return Response(
                {'error': 'Invalid classroom ID'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        if classroom.password != password:
            return Response(
                {'error': 'Invalid password'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is a student
        if hasattr(request.user, 'role') and request.user.role != 'STUDENT':
            return Response(
                {'error': 'Only students can join classrooms'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Create or update membership
        membership, created = ClassroomMembership.objects.get_or_create(
            classroom=classroom,
            student=request.user,
            defaults={'is_active': True}
        )
        
        if not created and not membership.is_active:
            membership.is_active = True
            membership.save()
        
        return Response({
            'message': 'Successfully joined classroom',
            'classroom': ClassroomSerializer(classroom).data
        })

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all members of a classroom."""
        classroom = self.get_object()
        memberships = ClassroomMembership.objects.filter(
            classroom=classroom, 
            is_active=True
        ).select_related('student')
        
        serializer = ClassroomMembershipSerializer(memberships, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def exams(self, request, pk=None):
        """Get all exams in a classroom."""
        classroom = self.get_object()
        exams = classroom.exams.all()
        serializer = ExamSerializer(exams, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get exam results for all students in the classroom."""
        classroom = self.get_object()
        # Import here to avoid circular imports
        from sessions.models import ExamSession
        
        results = []
        for exam in classroom.exams.filter(is_published=True):
            exam_results = {
                'exam_id': exam.id,
                'exam_title': exam.title,
                'student_results': []
            }
            
            sessions = ExamSession.objects.filter(exam=exam).select_related('student')
            for session in sessions:
                exam_results['student_results'].append({
                    'student_id': session.student.id,
                    'student_name': session.student.username,
                    'status': session.status,
                    'total_marks': session.total_marks,
                    'violation_count': session.violation_count,
                    'started_at': session.started_at,
                    'ended_at': session.ended_at,
                })
            
            results.append(exam_results)
        
        return Response(results)


class ExamViewSet(viewsets.ModelViewSet):
    queryset = Exam.objects.all().select_related('teacher', 'classroom')
    serializer_class = ExamSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'start_datetime']
    permission_classes = [ExamReadPermission]

    def get_queryset(self):
        user = self.request.user
        qs = super().get_queryset()
        role = getattr(user, 'role', None)
        
        if role in ('ADMIN', 'TEACHER'):
            if role == 'TEACHER':
                return qs.filter(teacher=user)
            return qs
        
        # Students can see all published exams (no classroom restriction)
        return qs.filter(is_published=True)

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish an exam to make it available to students."""
        exam = self.get_object()
        
        if not exam.questions.exists():
            return Response(
                {'error': 'Cannot publish exam without questions'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        exam.is_published = True
        exam.save()
        
        return Response({'message': 'Exam published successfully'})

    @action(detail=True, methods=['post'])
    def unpublish(self, request, pk=None):
        """Unpublish an exam."""
        exam = self.get_object()
        exam.is_published = False
        exam.save()
        
        return Response({'message': 'Exam unpublished successfully'})


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrTeacher]

    def get_queryset(self):
        exam_id = self.kwargs.get('exam_pk') or self.kwargs.get('exam_id')
        return Question.objects.filter(exam_id=exam_id)

    def perform_create(self, serializer):
        exam_id = self.kwargs.get('exam_pk') or self.kwargs.get('exam_id')
        serializer.save(exam_id=exam_id)

    @action(detail=False, methods=['post'])
    def bulk_create(self, request, exam_pk=None):
        """Create multiple questions at once."""
        exam_id = exam_pk
        questions_data = request.data.get('questions', [])
        
        if not questions_data:
            return Response(
                {'error': 'No questions provided'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_questions = []
        for question_data in questions_data:
            question_data['exam'] = exam_id
            serializer = self.get_serializer(data=question_data)
            if serializer.is_valid():
                question = serializer.save(exam_id=exam_id)
                created_questions.append(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(created_questions, status=status.HTTP_201_CREATED)


class AdminSettingsViewSet(viewsets.ModelViewSet):
    queryset = AdminSettings.objects.all()
    serializer_class = AdminSettingsSerializer
    permission_classes = [IsAdmin]
    http_method_names = ['get', 'post', 'patch']
from django.shortcuts import render

# Create your views here.
