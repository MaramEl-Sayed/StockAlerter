from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from .models import Alert, AlertHistory
from .serializers import (
    AlertSerializer, AlertHistorySerializer, AlertCreateSerializer, AlertUpdateSerializer
)
from .services import check_all_alerts

class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user alerts"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Return alerts for the current user"""
        return Alert.objects.filter(user=self.request.user).select_related('stock')
    
    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'create':
            return AlertCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return AlertUpdateSerializer
        return AlertSerializer
    
    def perform_create(self, serializer):
        """Create alert and set user automatically"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def check_condition(self, request, pk=None):
        """Manually check if an alert condition is met"""
        alert = self.get_object()
        
        # Check the alert condition directly
        try:
            # This will check all alerts, but we can enhance it later
            result = check_all_alerts()
            return Response({
                'message': 'Alert condition check completed',
                'result': result
            })
        except Exception as e:
            return Response({
                'error': f'Failed to check alert condition: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def toggle_active(self, request, pk=None):
        """Toggle alert active status"""
        alert = self.get_object()
        alert.is_active = not alert.is_active
        alert.save()
        
        return Response({
            'message': f"Alert {'activated' if alert.is_active else 'deactivated'}",
            'is_active': alert.is_active
        })
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get only active alerts"""
        active_alerts = self.get_queryset().filter(is_active=True, status='active')
        serializer = self.get_serializer(active_alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def triggered(self, request):
        """Get triggered alerts"""
        triggered_alerts = self.get_queryset().filter(status='triggered')
        serializer = self.get_serializer(triggered_alerts, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def reset_triggered(self, request):
        """Reset all triggered alerts back to active"""
        try:
            # Reset all triggered alerts for the current user
            triggered_alerts = self.get_queryset().filter(status='triggered')
            updated_count = triggered_alerts.update(status='active', is_active=True)
            
            return Response({
                'message': f'Reset {updated_count} triggered alerts successfully',
                'updated_count': updated_count
            })
        except Exception as e:
            return Response({
                'error': f'Failed to reset triggered alerts: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AlertHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing alert history"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AlertHistorySerializer
    
    def get_queryset(self):
        """Return alert history for the current user"""
        return AlertHistory.objects.filter(
            alert__user=self.request.user
        ).select_related('alert', 'alert__stock').order_by('-triggered_at')
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent alert history (last 30 days)"""
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        recent_history = self.get_queryset().filter(triggered_at__gte=thirty_days_ago)
        
        page = self.paginate_queryset(recent_history)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(recent_history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_stock(self, request):
        """Get alert history grouped by stock"""
        stock_symbol = request.query_params.get('symbol', '').upper()
        if not stock_symbol:
            return Response(
                {'error': 'Stock symbol is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        stock_history = self.get_queryset().filter(alert__stock__symbol=stock_symbol)
        serializer = self.get_serializer(stock_history, many=True)
        return Response(serializer.data)
