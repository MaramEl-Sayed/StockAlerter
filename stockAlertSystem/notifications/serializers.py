from rest_framework import serializers
from .models import Notification, EmailTemplate
from accounts.serializers import UserSerializer

class NotificationSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'user', 'user_details', 'alert_history', 'notification_type',
            'subject', 'message', 'status', 'sent_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'sent_at', 'created_at']

class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications"""
    class Meta:
        model = Notification
        fields = ['user', 'alert_history', 'notification_type', 'subject', 'message']

class EmailTemplateSerializer(serializers.ModelSerializer):
    """Serializer for email templates"""
    class Meta:
        model = EmailTemplate
        fields = ['id', 'name', 'subject', 'body', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    total_notifications = serializers.IntegerField()
    pending_notifications = serializers.IntegerField()
    sent_notifications = serializers.IntegerField()
    failed_notifications = serializers.IntegerField()
    email_notifications = serializers.IntegerField()
    console_notifications = serializers.IntegerField()
