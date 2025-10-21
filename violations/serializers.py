from rest_framework import serializers

from .models import Violation
from sessions.models import ExamSession


class ViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Violation
        fields = ['id', 'session', 'student', 'violation_type', 'timestamp', 'details', 'resolved', 'created_at']
        read_only_fields = ['student', 'created_at']


class ViolationLogSerializer(serializers.Serializer):
    session_id = serializers.IntegerField()
    violation_type = serializers.ChoiceField(choices=Violation.ViolationType.choices)
    timestamp = serializers.DateTimeField()
    details = serializers.CharField(allow_blank=True, required=False, max_length=512)

