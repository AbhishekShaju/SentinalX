from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
import string
import random

User = settings.AUTH_USER_MODEL


class Classroom(models.Model):
    """Classroom created by a teacher for conducting exams."""
    
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classrooms')
    name = models.CharField(max_length=255)
    classroom_id = models.CharField(max_length=20, unique=True)
    password = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.classroom_id:
            self.classroom_id = self.generate_classroom_id()
        super().save(*args, **kwargs)

    def generate_classroom_id(self):
        """Generate a unique classroom ID."""
        while True:
            classroom_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
            if not Classroom.objects.filter(classroom_id=classroom_id).exists():
                return classroom_id

    def __str__(self):
        return f"{self.name} ({self.classroom_id})"

    class Meta:
        ordering = ["-created_at"]


class ClassroomMembership(models.Model):
    """Tracks which students have joined which classrooms."""
    
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='memberships')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classroom_memberships')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('classroom', 'student')
        ordering = ["-joined_at"]

    def __str__(self):
        return f"{self.student.username} in {self.classroom.name}"


class Exam(models.Model):
    """Exam created by a teacher.

    Contains timing and violation settings. Duration is in minutes.
    Now includes password protection instead of classroom-based access.
    """

    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exams')
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='exams', null=True, blank=True)  # Will be removed later
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    password = models.CharField(max_length=255, help_text='Password required for students to access this exam')
    duration_minutes = models.PositiveIntegerField(default=60)
    violation_limit = models.PositiveIntegerField(default=5)
    start_datetime = models.DateTimeField(null=True, blank=True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.title} ({self.duration_minutes}m)"


class Question(models.Model):
    """Question for an exam.

    Supports MCQ and True/False questions only.
    For MCQ, `choices` is a JSON list of strings and `correct_answer` stores the correct index (0-based).
    For True/False, `correct_answer` stores 1 for True, 0 for False.
    """

    class QuestionType(models.TextChoices):
        MCQ = 'MCQ', _('Multiple Choice')
        TRUE_FALSE = 'TRUE_FALSE', _('True/False')

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    type = models.CharField(max_length=20, choices=QuestionType.choices)
    text = models.TextField()
    choices = models.JSONField(null=True, blank=True, help_text='For MCQ questions, list of choices')
    correct_answer = models.TextField(null=True, blank=True, help_text='Correct answer or explanation')
    marks = models.FloatField(default=1.0)
    order = models.PositiveIntegerField(default=0)
    explanation = models.TextField(blank=True, help_text='Explanation for the correct answer')

    class Meta:
        ordering = ["order", "id"]

    def __str__(self) -> str:  # pragma: no cover
        return f"Q{self.id} ({self.type}): {self.text[:50]}..."


class AdminSettings(models.Model):
    """Global settings managed by Admin.

    Currently holds the default violation limit. If no row exists, fallback to
    Django setting CHEAT_DETECTION_DEFAULT_VIOLATION_LIMIT.
    """

    default_violation_limit = models.PositiveIntegerField(default=5)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"AdminSettings(default_violation_limit={self.default_violation_limit})"

    @classmethod
    def get_default_violation_limit(cls) -> int:
        from django.conf import settings as dj_settings

        instance = cls.objects.order_by('-updated_at').first()
        if instance:
            return instance.default_violation_limit
        return getattr(dj_settings, 'CHEAT_DETECTION_DEFAULT_VIOLATION_LIMIT', 5)
from django.db import models

# Create your models here.
