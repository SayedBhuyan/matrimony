import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model using email as the authentication identifier.

    Stores account-level information only. Matrimonial profile data
    lives in the separate Profile model (profiles app).
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        'email address',
        unique=True,
        error_messages={
            'unique': 'A user with that email address already exists.',
        },
    )
    phone = models.CharField(
        'phone number',
        max_length=20,
        blank=True,
        help_text='Optional. For future SMS verification.',
    )

    # Account status
    is_active = models.BooleanField(
        'active',
        default=True,
        help_text='Designates whether this user should be treated as active.',
    )
    is_staff = models.BooleanField(
        'staff status',
        default=False,
        help_text='Designates whether the user can log into the admin site.',
    )
    is_email_verified = models.BooleanField(
        'email verified',
        default=False,
        help_text='Designates whether the user has verified their email address.',
    )

    # Timestamps
    date_joined = models.DateTimeField('date joined', default=timezone.now)
    last_activity = models.DateTimeField('last activity', null=True, blank=True)
    deactivated_at = models.DateTimeField(
        'deactivated at',
        null=True,
        blank=True,
        help_text='When the user deactivated their account. Null means active.',
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # Email is already required as USERNAME_FIELD

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['date_joined']),
            models.Index(fields=['is_active', 'is_email_verified']),
        ]

    def __str__(self):
        return self.email

    def get_short_name(self):
        """Return the email prefix as a short name."""
        return self.email.split('@')[0]

    def update_last_activity(self):
        """Update the last activity timestamp."""
        self.last_activity = timezone.now()
        self.save(update_fields=['last_activity'])
