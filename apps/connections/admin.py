from django.contrib import admin
from .models import Interest, Favorite, Block, Report


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'status', 'sent_at', 'responded_at')
    list_filter = ('status', 'sent_at', 'responded_at')
    search_fields = ('sender__email', 'receiver__email')
    readonly_fields = ('id', 'sent_at', 'responded_at')
    
    fieldsets = (
        ('Interest Details', {
            'fields': ('id', 'sender', 'receiver', 'status', 'message'),
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'responded_at'),
        }),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'profile__display_name')
    readonly_fields = ('id', 'created_at')


@admin.register(Block)
class BlockAdmin(admin.ModelAdmin):
    list_display = ('user', 'blocked_user', 'reason', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__email', 'blocked_user__email')
    readonly_fields = ('id', 'created_at')


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('reporter', 'reported_user', 'report_type', 'status', 'created_at')
    list_filter = ('status', 'report_type', 'created_at', 'reviewed_at')
    search_fields = ('reporter__email', 'reported_user__email', 'description')
    readonly_fields = ('id', 'created_at', 'reviewed_at')
    
    fieldsets = (
        ('Report Details', {
            'fields': ('id', 'reporter', 'reported_user', 'report_type', 'description', 'status'),
        }),
        ('Review Information', {
            'fields': ('reviewed_by', 'reviewed_at', 'admin_notes'),
        }),
        ('Timestamps', {
            'fields': ('created_at',),
        }),
    )
