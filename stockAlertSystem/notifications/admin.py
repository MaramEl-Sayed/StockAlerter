from django.contrib import admin
from .models import Notification, EmailTemplate

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'subject', 'status', 'sent_at', 'created_at']
    list_filter = ['notification_type', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'subject', 'message']
    readonly_fields = ['created_at', 'sent_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'alert_history', 'notification_type', 'subject', 'message')
        }),
        ('Status', {
            'fields': ('status', 'sent_at', 'error_message')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'subject', 'body']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active']
