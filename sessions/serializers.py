from typing import Any

from rest_framework import serializers

from exams.models import Exam, Question
from exams.serializers import ExamSerializer, QuestionSerializer
from users.serializers import UserSerializer
from .models import ExamSession, Answer


class AnswerSerializer(serializers.ModelSerializer):
    question = QuestionSerializer(read_only=True)
    
    class Meta:
        model = Answer
        fields = ['id', 'question', 'mcq_choice', 'short_text', 'marks_awarded']
        read_only_fields = ['marks_awarded']


class AnswerSubmitSerializer(serializers.Serializer):
    """Serializer for submitting answers (write-only)"""
    question_id = serializers.IntegerField(required=True)
    mcq_choice = serializers.IntegerField(required=False, allow_null=True)
    short_text = serializers.CharField(required=False, allow_blank=True, allow_null=True)


class ExamSessionSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    student = UserSerializer(read_only=True)
    answers = AnswerSerializer(many=True, read_only=True)
    score = serializers.FloatField(read_only=True)
    
    class Meta:
        model = ExamSession
        fields = [
            'id', 'exam', 'student', 'started_at', 'ended_at', 'status',
            'violation_count', 'total_marks', 'time_left', 'answers', 'score'
        ]
        read_only_fields = ['student', 'started_at', 'ended_at', 'status', 'violation_count', 'total_marks', 'time_left', 'score']


class ExamSessionSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for session lists without full related data"""
    score = serializers.FloatField(read_only=True)
    student = UserSerializer(read_only=True)
    exam = ExamSerializer(read_only=True)
    
    class Meta:
        model = ExamSession
        fields = [
            'id', 'exam', 'student', 'started_at', 'ended_at', 'status',
            'violation_count', 'total_marks', 'time_left', 'score'
        ]
        read_only_fields = ['student', 'started_at', 'ended_at', 'status', 'violation_count', 'total_marks', 'time_left', 'score']


class StartExamSerializer(serializers.Serializer):
    password = serializers.CharField(required=True, help_text="Password required to start the exam")
    
    def create(self, validated_data: dict[str, Any]) -> ExamSession:  # not used
        raise NotImplementedError

    def validate(self, attrs):
        exam = self.context['exam']
        password = attrs.get('password')
        
        if exam.password != password:
            raise serializers.ValidationError({'password': 'Incorrect exam password'})
        
        return attrs

    def save(self, **kwargs) -> ExamSession:
        request = self.context['request']
        user = request.user
        exam: Exam = self.context['exam']
        session = ExamSession.objects.create(exam=exam, student=user)
        session.update_time_left()
        session.save()
        return session


class SubmitExamSerializer(serializers.Serializer):
    answers = AnswerSubmitSerializer(many=True)

    def validate(self, attrs):
        session: ExamSession = self.context['session']
        # Allow submitting answers when session is ongoing or when it was terminated
        # (termination can occur due to violation limit); disallow if already completed.
        if session.status == ExamSession.Status.COMPLETED:
            raise serializers.ValidationError('This exam has already been submitted. Only one attempt is allowed per exam.')
        if session.status not in (ExamSession.Status.ONGOING, ExamSession.Status.TERMINATED):
            raise serializers.ValidationError('Session is not in a valid state for submission.')
        return attrs

    def save(self, **kwargs) -> ExamSession:
        data = self.validated_data
        session: ExamSession = self.context['session']
        answers_data = data['answers']

        # index questions for quick lookup
        q_map = {q.id: q for q in session.exam.questions.all()}
        total = 0.0

        for item in answers_data:
            # Get question ID from either 'question_id' or 'question' field
            question_id = item.get('question_id') or (item['question'].id if isinstance(item.get('question'), Question) else item.get('question'))
            q = q_map.get(question_id)
            if not q:
                continue
            ans, _ = Answer.objects.update_or_create(
                session=session, question=q,
                defaults={
                    'mcq_choice': item.get('mcq_choice'),
                    'short_text': item.get('short_text') or '',
                }
            )
            # Auto-mark MCQ
            if q.type == 'MCQ' and ans.mcq_choice is not None and q.correct_answer is not None:
                ans.marks_awarded = float(q.marks) if int(ans.mcq_choice) == int(q.correct_answer) else 0.0
                ans.save()
            total += ans.marks_awarded

        session.total_marks = total
        session.update_time_left()
        session.complete()
        session.save()
        return session

