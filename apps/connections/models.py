import uuid
from django.conf import settings
from django.db import models
from django.utils import timezone


class Interest(models.Model):
    """
    Matrimonial interest sent from one user to another.
    Supports various statuses to track the lifecycle of an interest.
    """
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),  # Sender cancelled
        ('withdrawn', 'Withdrawn'),  # Receiver withdrew after acceptance
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interests_sent',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='interests_received',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    message = models.TextField(
        blank=True,
        max_length=500,
        help_text='Optional message to accompany the interest.',
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'interest'
        verbose_name_plural = 'interests'
        constraints = [
            models.UniqueConstraint(
                fields=['sender', 'receiver'],
                condition=models.Q(status='pending'),
                name='unique_pending_interest',
            ),
            models.CheckConstraint(
                condition=~models.Q(sender=models.F('receiver')),
                name='interest_sender_receiver_different',
            ),
        ]
        indexes = [
            models.Index(fields=['receiver', 'status']),
            models.Index(fields=['sender', 'status']),
            models.Index(fields=['status', '-sent_at']),
        ]
    
    def __str__(self):
        return f"{self.sender.email} → {self.receiver.email} ({self.status})"


class Favorite(models.Model):
    """
    Allows users to save/shortlist profiles they're interested in.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    profile = models.ForeignKey(
        'profiles.Profile',
        on_delete=models.CASCADE,
        related_name='favorited_by',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'favorite'
        verbose_name_plural = 'favorites'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'profile'],
                name='unique_user_favorite_profile',
            ),
        ]
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.email} favorited {self.profile.display_name}"


class Block(models.Model):
    """
    Allows users to block other profiles from contacting them or seeing their profile.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_users',
    )
    blocked_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blocked_by',
    )
    reason = models.CharField(
        max_length=50,
        blank=True,
        help_text='Optional reason for blocking.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'block'
        verbose_name_plural = 'blocks'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'blocked_user'],
                name='unique_user_block',
            ),
            models.CheckConstraint(
                condition=~models.Q(user=models.F('blocked_user')),
                name='block_user_blocked_different',
            ),
        ]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['blocked_user']),
        ]
    
    def __str__(self):
        return f"{self.user.email} blocked {self.blocked_user.email}"


class Report(models.Model):
    """
    Allows users to report inappropriate profiles or behavior.
    """
    
    REPORT_TYPE_CHOICES = (
        ('fake_profile', 'Fake Profile'),
        ('inappropriate_content', 'Inappropriate Content'),
        ('harassment', 'Harassment'),
        ('scam', 'Scam / Fraud'),
        ('offensive_language', 'Offensive Language'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending Review'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_filed',
    )
    reported_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_against',
    )
    report_type = models.CharField(
        max_length=30,
        choices=REPORT_TYPE_CHOICES,
    )
    description = models.TextField(
        max_length=1000,
        help_text='Detailed description of the issue.',
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_reviewed',
    )
    admin_notes = models.TextField(
        blank=True,
        help_text='Admin notes on the resolution.',
    )
    
    class Meta:
        verbose_name = 'report'
        verbose_name_plural = 'reports'
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(reporter=models.F('reported_user')),
                name='report_reporter_reported_different',
            ),
        ]
        indexes = [
            models.Index(fields=['reported_user', 'status']),
            models.Index(fields=['status', '-created_at']),
        ]
    
    def __str__(self):
        return f"Report #{self.id}: {self.get_report_type_display()} by {self.reporter.email}"
