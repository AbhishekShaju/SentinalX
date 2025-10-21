from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from sessions.models import ExamSession

User = settings.AUTH_USER_MODEL


class Violation(models.Model):
    class ViolationType(models.TextChoices):
        # Face detection violations
        MULTIPLE_FACES = 'MULTIPLE_FACES', _('Multiple Faces')
        NO_FACE_DETECTED = 'NO_FACE_DETECTED', _('No Face Detected')
        HEAD_MOVEMENT = 'HEAD_MOVEMENT', _('Head Movement')
        LOOKING_AWAY = 'LOOKING_AWAY', _('Looking Away')
        CAMERA_ACCESS_DENIED = 'CAMERA_ACCESS_DENIED', _('Camera Access Denied')
        
        # Tab/Window violations
        TAB_SWITCH = 'TAB_SWITCH', _('Tab Switch')
        WINDOW_BLUR = 'WINDOW_BLUR', _('Window Blur')
        
        # Keyboard violations
        COPY_PASTE = 'COPY_PASTE', _('Copy/Paste')
        KEYBOARD_SHORTCUT = 'KEYBOARD_SHORTCUT', _('Keyboard Shortcut')
        FUNCTION_KEY = 'FUNCTION_KEY', _('Function Key')
        ALT_TAB = 'ALT_TAB', _('Alt+Tab')
        PASTE_ACTION = 'PASTE_ACTION', _('Paste Action')
        COPY_ACTION = 'COPY_ACTION', _('Copy Action')
        RIGHT_CLICK = 'RIGHT_CLICK', _('Right Click')
        
        # Audio violations
        AUDIO_VIOLATION = 'AUDIO_VIOLATION', _('Audio Violation')
        
        # Other
        OTHER = 'OTHER', _('Other')

    session = models.ForeignKey(ExamSession, on_delete=models.CASCADE, related_name='violations')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='violations')
    violation_type = models.CharField(max_length=32, choices=ViolationType.choices)
    timestamp = models.DateTimeField()
    details = models.CharField(max_length=512, blank=True, default='')
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.violation_type} @ {self.timestamp}"
from django.db import models

# Create your models here.
