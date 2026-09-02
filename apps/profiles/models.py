import os
import uuid
from datetime import date
from django.conf import settings
from django.db import models
from django.utils import timezone

from .validators import validate_profile_photo


def profile_photo_upload_path(instance, filename):
    """Generate isolated and non-predictable upload path for photos."""
    ext = os.path.splitext(filename)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}{ext}"
    return f"profile_photos/{instance.profile.user.id}/{unique_filename}"


class Profile(models.Model):
    """
    Core matrimonial profile entity attached 1-to-1 to a User.
    Contains basic demographic and identity fields.
    """

    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )

    MARITAL_STATUS_CHOICES = (
        ('never_married', 'Never Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
        ('annulled', 'Annulled'),
        ('awaiting_divorce', 'Awaiting Divorce'),
    )

    PROFILE_CREATED_FOR_CHOICES = (
        ('self', 'Self'),
        ('son', 'Son'),
        ('daughter', 'Daughter'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('friend', 'Friend'),
        ('relative', 'Relative'),
    )

    VISIBILITY_CHOICES = (
        ('public', 'Public (Visible to everyone)'),
        ('registered_only', 'Registered Members Only'),
        ('connections_only', 'Accepted Connections Only'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    display_name = models.CharField(
        'display name',
        max_length=100,
        help_text='Name displayed on your matrimonial profile.',
    )
    gender = models.CharField(
        'gender',
        max_length=10,
        choices=GENDER_CHOICES,
    )
    date_of_birth = models.DateField(
        'date of birth',
    )
    height_cm = models.PositiveSmallIntegerField(
        'height (cm)',
        null=True,
        blank=True,
        help_text='Height in centimeters (e.g. 175).',
    )
    marital_status = models.CharField(
        'marital status',
        max_length=20,
        choices=MARITAL_STATUS_CHOICES,
        default='never_married',
    )
    profile_created_for = models.CharField(
        'profile created for',
        max_length=20,
        choices=PROFILE_CREATED_FOR_CHOICES,
        default='self',
    )

    # Cultural & Religious background
    religion = models.CharField(
        'religion',
        max_length=50,
        default='Not Specified',
    )
    caste = models.CharField(
        'caste / community',
        max_length=50,
        blank=True,
    )
    sub_caste = models.CharField(
        'sub-caste',
        max_length=50,
        blank=True,
    )
    mother_tongue = models.CharField(
        'mother tongue',
        max_length=50,
        default='English',
    )

    # Location
    country = models.CharField(
        'country',
        max_length=100,
        default='United States',
    )
    state = models.CharField(
        'state / province',
        max_length=100,
        blank=True,
    )
    city = models.CharField(
        'city',
        max_length=100,
    )
    citizenship = models.CharField(
        'citizenship',
        max_length=100,
        blank=True,
    )

    # Bio
    about_me = models.TextField(
        'about me',
        max_length=2000,
        blank=True,
        help_text='Write a short introduction about yourself, your background, and what you value.',
    )

    # Privacy and Trust
    visibility = models.CharField(
        'profile visibility',
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='registered_only',
    )
    is_verified = models.BooleanField(
        'is verified',
        default=False,
        help_text='Verified by platform administrators.',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'matrimonial profile'
        verbose_name_plural = 'matrimonial profiles'
        indexes = [
            models.Index(fields=['gender', 'marital_status']),
            models.Index(fields=['religion', 'mother_tongue']),
            models.Index(fields=['country', 'city']),
            models.Index(fields=['is_verified', 'visibility']),
        ]

    def __str__(self):
        return f"{self.display_name} ({self.get_gender_display()})"

    @property
    def age(self):
        """Calculate current age in full years from date_of_birth."""
        if not self.date_of_birth:
            return None
        today = date.today()
        return today.year - self.date_of_birth.year - (
            (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
        )

    @property
    def height_formatted(self):
        """Format height in feet and inches alongside centimeters."""
        if not self.height_cm:
            return None
        inches_total = self.height_cm / 2.54
        feet = int(inches_total // 12)
        inches = int(round(inches_total % 12))
        if inches == 12:
            feet += 1
            inches = 0
        return f"{feet}'{inches}\" ({self.height_cm} cm)"

    @property
    def primary_photo(self):
        """Retrieve the primary approved photo or the first available approved photo."""
        primary = self.photos.filter(is_primary=True, is_approved=True).first()
        if primary:
            return primary
        return self.photos.filter(is_approved=True).first()


class ProfileView(models.Model):
    """A unique profile visit per viewer and calendar day."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='views')
    viewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile_views')
    viewed_date = models.DateField(default=date.today)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['profile', 'viewer', 'viewed_date'],
                name='unique_profile_viewer_view',
            ),
        ]
        indexes = [models.Index(fields=['profile', '-viewed_at'])]


class EducationDetail(models.Model):
    """Educational qualifications of a matrimonial candidate."""

    EDUCATION_LEVEL_CHOICES = (
        ('doctorate', 'Doctorate / Ph.D.'),
        ('masters', "Master's Degree"),
        ('bachelors', "Bachelor's Degree"),
        ('diploma', 'Diploma / Associate Degree'),
        ('high_school', 'High School'),
        ('trade_school', 'Vocational / Trade School'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='education',
    )
    highest_education = models.CharField(
        'highest education',
        max_length=20,
        choices=EDUCATION_LEVEL_CHOICES,
        default='bachelors',
    )
    ug_degree = models.CharField(
        'undergraduate degree',
        max_length=100,
        blank=True,
    )
    pg_degree = models.CharField(
        'postgraduate degree',
        max_length=100,
        blank=True,
    )
    institution = models.CharField(
        'college / university',
        max_length=150,
        blank=True,
    )
    field_of_study = models.CharField(
        'field of study / major',
        max_length=100,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Education: {self.get_highest_education_display()} - {self.profile.display_name}"


class ProfessionDetail(models.Model):
    """Career and economic background of a matrimonial candidate."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='profession',
    )
    occupation = models.CharField(
        'occupation / job title',
        max_length=100,
    )
    industry = models.CharField(
        'industry / sector',
        max_length=100,
        blank=True,
    )
    employer = models.CharField(
        'company / employer',
        max_length=150,
        blank=True,
    )
    annual_income = models.CharField(
        'annual income range',
        max_length=60,
        blank=True,
        help_text='e.g. "$75,000 - $100,000" or "INR 15-20 Lakhs"',
    )
    working_city = models.CharField(
        'working city',
        max_length=100,
        blank=True,
    )
    working_country = models.CharField(
        'working country',
        max_length=100,
        blank=True,
    )
    income_visible = models.BooleanField(
        'make income visible',
        default=True,
        help_text='If unchecked, income will only be visible to accepted connections.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profession: {self.occupation} - {self.profile.display_name}"


class FamilyDetail(models.Model):
    """Family structure and values."""

    FAMILY_TYPE_CHOICES = (
        ('nuclear', 'Nuclear Family'),
        ('joint', 'Joint Family'),
        ('other', 'Other'),
    )

    FAMILY_VALUES_CHOICES = (
        ('traditional', 'Traditional'),
        ('moderate', 'Moderate'),
        ('liberal', 'Liberal'),
    )

    FAMILY_STATUS_CHOICES = (
        ('middle_class', 'Middle Class'),
        ('upper_middle_class', 'Upper Middle Class'),
        ('rich', 'High / Affluent Class'),
        ('other', 'Other'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='family',
    )
    family_type = models.CharField(
        'family type',
        max_length=20,
        choices=FAMILY_TYPE_CHOICES,
        default='nuclear',
    )
    family_values = models.CharField(
        'family values',
        max_length=20,
        choices=FAMILY_VALUES_CHOICES,
        default='moderate',
    )
    family_status = models.CharField(
        'family financial status',
        max_length=25,
        choices=FAMILY_STATUS_CHOICES,
        blank=True,
    )
    father_occupation = models.CharField(
        "father's occupation",
        max_length=100,
        blank=True,
    )
    mother_occupation = models.CharField(
        "mother's occupation",
        max_length=100,
        blank=True,
    )
    brothers_count = models.PositiveSmallIntegerField(
        'number of brothers',
        default=0,
    )
    sisters_count = models.PositiveSmallIntegerField(
        'number of sisters',
        default=0,
    )
    living_with_parents = models.BooleanField(
        'living with parents',
        default=False,
    )
    family_location = models.CharField(
        'family native / base location',
        max_length=150,
        blank=True,
    )
    about_family = models.TextField(
        'about family',
        max_length=1000,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Family: {self.profile.display_name}"


class LifestyleDetail(models.Model):
    """Personal habits, diet, and lifestyle choices."""

    DIET_CHOICES = (
        ('vegetarian', 'Vegetarian'),
        ('non_vegetarian', 'Non-Vegetarian'),
        ('eggetarian', 'Eggetarian'),
        ('vegan', 'Vegan'),
        ('halal', 'Halal Only'),
        ('jain', 'Jain Diet'),
        ('other', 'Other'),
    )

    HABIT_CHOICES = (
        ('never', 'Never'),
        ('occasionally', 'Occasionally'),
        ('socially', 'Socially'),
        ('regularly', 'Regularly'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='lifestyle',
    )
    diet = models.CharField(
        'dietary preferences',
        max_length=20,
        choices=DIET_CHOICES,
        default='non_vegetarian',
    )
    smoking = models.CharField(
        'smoking habit',
        max_length=20,
        choices=HABIT_CHOICES,
        default='never',
    )
    drinking = models.CharField(
        'drinking habit',
        max_length=20,
        choices=HABIT_CHOICES,
        default='never',
    )
    hobbies = models.CharField(
        'hobbies & interests',
        max_length=255,
        blank=True,
        help_text='e.g. Photography, Hiking, Reading, Cooking',
    )
    spoken_languages = models.CharField(
        'spoken languages',
        max_length=255,
        blank=True,
        help_text='e.g. English, Bengali, Hindi, Spanish',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lifestyle: {self.profile.display_name}"


class PartnerPreference(models.Model):
    """Desired characteristics and expectations in a prospective spouse."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='partner_preference',
    )
    min_age = models.PositiveSmallIntegerField(
        'minimum age',
        default=18,
    )
    max_age = models.PositiveSmallIntegerField(
        'maximum age',
        default=45,
    )
    min_height_cm = models.PositiveSmallIntegerField(
        'minimum height (cm)',
        null=True,
        blank=True,
    )
    max_height_cm = models.PositiveSmallIntegerField(
        'maximum height (cm)',
        null=True,
        blank=True,
    )
    preferred_marital_status = models.CharField(
        'preferred marital status',
        max_length=100,
        blank=True,
        help_text='Comma-separated choices or leave empty for any.',
    )
    preferred_religion = models.CharField(
        'preferred religion',
        max_length=100,
        blank=True,
    )
    preferred_mother_tongue = models.CharField(
        'preferred mother tongue',
        max_length=100,
        blank=True,
    )
    preferred_education = models.CharField(
        'preferred education',
        max_length=100,
        blank=True,
    )
    preferred_occupation = models.CharField(
        'preferred occupation',
        max_length=100,
        blank=True,
    )
    preferred_country = models.CharField(
        'preferred country',
        max_length=100,
        blank=True,
    )
    preferred_diet = models.CharField(
        'preferred diet',
        max_length=100,
        blank=True,
    )
    notes = models.TextField(
        'partner expectations / notes',
        max_length=1000,
        blank=True,
        help_text='Specific qualities or values you cherish in a prospective partner.',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Partner Preferences for {self.profile.display_name}"


class ProfilePhoto(models.Model):
    """Individual photo associated with a matrimonial profile."""

    VISIBILITY_CHOICES = (
        ('public', 'Visible to All Members'),
        ('connections_only', 'Visible to Accepted Connections Only'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='photos',
    )
    image = models.ImageField(
        upload_to=profile_photo_upload_path,
        validators=[validate_profile_photo],
    )
    caption = models.CharField(
        'photo caption',
        max_length=100,
        blank=True,
    )
    is_primary = models.BooleanField(
        'is primary photo',
        default=False,
    )
    is_approved = models.BooleanField(
        'approved by moderation',
        default=True,
    )
    order = models.PositiveSmallIntegerField(
        'display order',
        default=0,
    )
    visibility = models.CharField(
        'photo privacy',
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'profile photo'
        verbose_name_plural = 'profile photos'
        ordering = ['-is_primary', 'order', '-created_at']

    def __str__(self):
        return f"Photo ({'Primary' if self.is_primary else 'Additional'}) - {self.profile.display_name}"

    def save(self, *args, **kwargs):
        # If this is set as primary, unmark other primary photos for this profile
        if self.is_primary:
            ProfilePhoto.objects.filter(
                profile=self.profile,
                is_primary=True,
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
