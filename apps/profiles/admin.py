from django.contrib import admin
from django.utils.html import format_html
from .models import (
    EducationDetail,
    FamilyDetail,
    LifestyleDetail,
    PartnerPreference,
    ProfessionDetail,
    Profile,
    ProfilePhoto,
)


class EducationInline(admin.StackedInline):
    model = EducationDetail
    extra = 0


class ProfessionInline(admin.StackedInline):
    model = ProfessionDetail
    extra = 0


class FamilyInline(admin.StackedInline):
    model = FamilyDetail
    extra = 0


class LifestyleInline(admin.StackedInline):
    model = LifestyleDetail
    extra = 0


class PartnerPreferenceInline(admin.StackedInline):
    model = PartnerPreference
    extra = 0


class ProfilePhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 0
    fields = ('photo_preview', 'image', 'is_primary', 'is_approved', 'visibility', 'order')
    readonly_fields = ('photo_preview',)

    def photo_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url
            )
        return 'No image'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'avatar_thumbnail',
        'display_name',
        'gender',
        'age_display',
        'religion',
        'city',
        'country',
        'is_verified',
        'visibility',
        'created_at',
    )
    list_filter = (
        'gender',
        'marital_status',
        'religion',
        'is_verified',
        'visibility',
        'country',
    )
    search_fields = ('display_name', 'user__email', 'city', 'state', 'caste')
    ordering = ('-created_at',)
    inlines = [
        EducationInline,
        ProfessionInline,
        FamilyInline,
        LifestyleInline,
        PartnerPreferenceInline,
        ProfilePhotoInline,
    ]

    def avatar_thumbnail(self, obj):
        primary = obj.primary_photo
        if primary and primary.image:
            return format_html(
                '<img src="{}" style="width: 40px; height: 40px; object-fit: cover; border-radius: 50%;" />',
                primary.image.url
            )
        return '👤'
    avatar_thumbnail.short_description = 'Photo'

    def age_display(self, obj):
        return obj.age or '-'
    age_display.short_description = 'Age'


@admin.register(ProfilePhoto)
class ProfilePhotoAdmin(admin.ModelAdmin):
    list_display = (
        'photo_preview',
        'profile',
        'is_primary',
        'is_approved',
        'visibility',
        'created_at',
    )
    list_filter = ('is_approved', 'is_primary', 'visibility')
    search_fields = ('profile__display_name', 'profile__user__email')

    def photo_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 8px;" />',
                obj.image.url
            )
        return 'No image'
    photo_preview.short_description = 'Preview'
