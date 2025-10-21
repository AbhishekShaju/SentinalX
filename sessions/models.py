from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from exams.models import Exam, Question

User = settings.AUTH_USER_MODEL


class ExamSession(models.Model):
    class Status(models.TextChoices):
        ONGOING = 'ONGOING', _('Ongoing')
        COMPLETED = 'COMPLETED', _('Completed')
        TERMINATED = 'TERMINATED', _('Terminated')

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='sessions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exam_sessions')
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ONGOING)
    violation_count = models.PositiveIntegerField(default=0)
    total_marks = models.FloatField(default=0.0)
    time_left = models.PositiveIntegerField(default=0, help_text='Remaining seconds when last updated')

    class Meta:
        # Ensure only one completed session per student per exam
        constraints = [
            models.UniqueConstraint(
                fields=['exam', 'student'],
                condition=models.Q(status='COMPLETED'),
                name='unique_completed_session_per_student_exam'
            )
        ]
        indexes = [
            models.Index(fields=['exam', 'student', 'status']),
            models.Index(fields=['-started_at']),
        ]

    def update_time_left(self) -> None:
        duration_seconds = int(self.exam.duration_minutes) * 60
        elapsed = int((timezone.now() - self.started_at).total_seconds())
        remaining = max(0, duration_seconds - max(elapsed, 0))
        self.time_left = remaining

    def complete(self) -> None:
        self.status = self.Status.COMPLETED
        self.ended_at = timezone.now()

    def terminate(self) -> None:
        self.status = self.Status.TERMINATED
        self.ended_at = timezone.now()

    @property
    def score(self) -> float:
        """Calculate total score from all answers"""
        return self.answers.aggregate(total=models.Sum('marks_awarded'))['total'] or 0.0


class Answer(models.Model):
    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    # For MCQ we store selected index; for short answer we store text
    mcq_choice = models.IntegerField(null=True, blank=True)
    short_text = models.TextField(blank=True, default='')
    marks_awarded = models.FloatField(default=0.0)

    class Meta:
        unique_together = ('session', 'question')
from django.db import models

# Create your models here.
