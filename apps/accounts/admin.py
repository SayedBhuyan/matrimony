from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for the custom User model."""

    list_display = (
        'email',
        'is_active',
        'is_email_verified',
        'is_staff',
        'date_joined',
        'last_activity',
    )
    list_filter = (
        'is_active',
        'is_staff',
        'is_superuser',
        'is_email_verified',
        'date_joined',
    )
    search_fields = ('email', 'phone')
    ordering = ('-date_joined',)

    # Fieldsets for the change form
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('phone',)}),
        ('Status', {
            'fields': (
                'is_active',
                'is_email_verified',
                'deactivated_at',
            ),
        }),
        ('Permissions', {
            'fields': (
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ),
        }),
        ('Important dates', {'fields': ('date_joined', 'last_activity')}),
    )

    # Fieldsets for the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'usable_password', 'password1', 'password2'),
        }),
    )

    readonly_fields = ('date_joined', 'last_activity')
