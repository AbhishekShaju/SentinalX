from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model with role-based access control.

    Extends Django's AbstractUser to include a role field and optional
    profile information. Roles are enforced via DRF permissions.
    """

    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Admin')
        TEACHER = 'TEACHER', _('Teacher')
        STUDENT = 'STUDENT', _('Student')

    role: models.CharField = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        help_text=_('Role of the user for permissions and access control.'),
    )

    # Optional profile fields
    organization: models.CharField = models.CharField(
        max_length=255, blank=True, default=''
    )
    display_name: models.CharField = models.CharField(
        max_length=255, blank=True, default=''
    )

    def __str__(self) -> str:  # pragma: no cover - simple representation
        return f"{self.username} ({self.role})"

# Create your models here.
