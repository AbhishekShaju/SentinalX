from typing import Any

from rest_framework import serializers

from .models import Exam, Question, AdminSettings, Classroom, ClassroomMembership


class ClassroomSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField(read_only=True)
    member_count = serializers.SerializerMethodField(read_only=True)
    exam_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Classroom
        fields = [
            'id', 'teacher', 'teacher_name', 'name', 'classroom_id', 'password', 
            'description', 'is_active', 'created_at', 'updated_at', 'member_count', 'exam_count'
        ]
        read_only_fields = ['teacher', 'classroom_id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def get_teacher_name(self, obj: Classroom) -> str:
        return getattr(obj.teacher, 'username', '')

    def get_member_count(self, obj: Classroom) -> int:
        return obj.memberships.filter(is_active=True).count()

    def get_exam_count(self, obj: Classroom) -> int:
        return obj.exams.count()

    def create(self, validated_data: dict[str, Any]) -> Classroom:
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None:
            raise serializers.ValidationError('Missing request user')
        return Classroom.objects.create(teacher=user, **validated_data)


class ClassroomMembershipSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    classroom_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ClassroomMembership
        fields = ['id', 'classroom', 'student', 'student_name', 'classroom_name', 'joined_at', 'is_active']
        read_only_fields = ['joined_at']

    def get_student_name(self, obj: ClassroomMembership) -> str:
        return getattr(obj.student, 'username', '')

    def get_classroom_name(self, obj: ClassroomMembership) -> str:
        return getattr(obj.classroom, 'name', '')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'type', 'text', 'choices', 'correct_answer', 'marks', 'order', 'explanation']

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        qtype = attrs.get('type', getattr(self.instance, 'type', None))
        choices = attrs.get('choices', getattr(self.instance, 'choices', None))
        correct = attrs.get('correct_answer', getattr(self.instance, 'correct_answer', None))
        
        if qtype == 'MCQ':
            if not isinstance(choices, list) or len(choices) < 2:
                raise serializers.ValidationError('MCQ must have at least two choices.')
            if correct is None or not (0 <= int(correct) < len(choices)):
                raise serializers.ValidationError('correct_answer must be a valid index for choices.')
        elif qtype == 'TRUE_FALSE':
            # For True/False questions, choices should be ['True', 'False']
            if not choices:
                attrs['choices'] = ['True', 'False']
            if correct is not None and correct not in ['0', '1', 0, 1]:
                raise serializers.ValidationError('correct_answer for True/False must be 0 or 1.')
        # For SHORT_ANSWER and ESSAY, no specific validation needed
        return attrs


class ExamSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    teacher_name = serializers.SerializerMethodField(read_only=True)
    question_count = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Exam
        fields = [
            'id', 'teacher', 'teacher_name', 'title', 'description', 'password',
            'duration_minutes', 'violation_limit', 'start_datetime', 'end_datetime', 'is_published', 
            'created_at', 'updated_at', 'questions', 'question_count'
        ]
        read_only_fields = ['teacher', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}  # Don't expose password in responses
        }

    def get_teacher_name(self, obj: Exam) -> str:
        return getattr(obj.teacher, 'username', '')

    def get_question_count(self, obj: Exam) -> int:
        return obj.questions.count()

    def create(self, validated_data: dict[str, Any]) -> Exam:
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None:
            raise serializers.ValidationError('Missing request user')
        # default violation limit if not provided
        if 'violation_limit' not in validated_data or validated_data['violation_limit'] is None:
            validated_data['violation_limit'] = AdminSettings.get_default_violation_limit()
        return Exam.objects.create(teacher=user, **validated_data)


class AdminSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminSettings
        fields = ['id', 'default_violation_limit', 'updated_at']
        read_only_fields = ['id', 'updated_at']

