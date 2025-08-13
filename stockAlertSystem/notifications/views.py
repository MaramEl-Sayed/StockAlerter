from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Notification, EmailTemplate
from .serializers import (
    NotificationSerializer, 
    NotificationCreateSerializer, 
    EmailTemplateSerializer,
    NotificationStatsSerializer
)
from .services import send_email_notification

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user notifications"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return notifications for the current user"""
        return Notification.objects.filter(user=self.request.user).select_related('alert_history')
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def perform_create(self, serializer):
        """Create notification and set user automatically"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending notifications"""
        pending_notifications = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(pending_notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def sent(self, request):
        """Get sent notifications"""
        sent_notifications = self.get_queryset().filter(status='sent')
        serializer = self.get_serializer(sent_notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def failed(self, request):
        """Get failed notifications"""
        failed_notifications = self.get_queryset().filter(status='failed')
        serializer = self.get_serializer(failed_notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resend(self, request, pk=None):
        """Resend a failed notification"""
        notification = self.get_object()
        
        if notification.status != 'failed':
            return Response(
                {'error': 'Only failed notifications can be resent'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Reset status and try to send again
            notification.status = 'pending'
            notification.error_message = None
            notification.save()
            
            # Send notification
            if notification.notification_type == 'email':
                send_email_notification.delay(
                    notification.user.id,
                    notification.subject,
                    notification.message,
                    notification.alert_history.id if notification.alert_history else None
                )
            
            return Response({'message': 'Notification resent successfully'})
            
        except Exception as e:
            return Response(
                {'error': f'Failed to resend notification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['post'])
    def send_test_notification(self, request):
        """Send a test notification to the current user"""
        notification_type = request.data.get('type', 'email')
        subject = request.data.get('subject', 'Test Notification')
        message = request.data.get('message', 'This is a test notification from Stock Alert System')
        
        try:
            # Create test notification
            notification = Notification.objects.create(
                user=request.user,
                notification_type=notification_type,
                subject=subject,
                message=message,
                status='pending'
            )
            
            # Send notification
            if notification_type == 'email':
                send_email_notification.delay(
                    request.user.id,
                    subject,
                    message
                )
            
            return Response({
                'message': 'Test notification sent successfully',
                'notification_id': notification.id
            })
            
        except Exception as e:
            return Response(
                {'error': f'Failed to send test notification: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def notification_stats(self, request):
        """Get notification statistics for the current user"""
        queryset = self.get_queryset()
        
        stats = {
            'total_notifications': queryset.count(),
            'pending_notifications': queryset.filter(status='pending').count(),
            'sent_notifications': queryset.filter(status='sent').count(),
            'failed_notifications': queryset.filter(status='failed').count(),
            'email_notifications': queryset.filter(notification_type='email').count(),
            'console_notifications': queryset.filter(notification_type='console').count(),
        }
        
        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)

class EmailTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for managing email templates"""
    permission_classes = [permissions.IsAuthenticated]
    queryset = EmailTemplate.objects.filter(is_active=True)
    serializer_class = EmailTemplateSerializer
    
    def get_permissions(self):
        """Allow read-only access to all authenticated users, write access to admin only"""
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    @action(detail=False, methods=['get'])
    def by_name(self, request):
        """Get email template by name"""
        template_name = request.query_params.get('name')
        if not template_name:
            return Response(
                {'error': 'Template name is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            template = EmailTemplate.objects.get(name=template_name, is_active=True)
            serializer = self.get_serializer(template)
            return Response(serializer.data)
        except EmailTemplate.DoesNotExist:
            return Response(
                {'error': 'Template not found'},
                status=status.HTTP_404_NOT_FOUND
            )

class NotificationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing notification history"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    
    def get_queryset(self):
        """Return notification history for the current user"""
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('alert_history').order_by('-created_at')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications (last 30 days)"""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_notifications = self.get_queryset().filter(created_at__gte=thirty_days_ago)
        
        page = self.paginate_queryset(recent_notifications)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(recent_notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get notifications by type"""
        notification_type = request.query_params.get('type')
        if not notification_type:
            return Response(
                {'error': 'Notification type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        type_notifications = self.get_queryset().filter(notification_type=notification_type)
        serializer = self.get_serializer(type_notifications, many=True)
        return Response(serializer.data)
