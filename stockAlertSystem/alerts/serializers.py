from rest_framework import serializers
from .models import Alert, AlertHistory
from stocks.serializers import StockSerializer
from accounts.serializers import UserSerializer

class AlertSerializer(serializers.ModelSerializer):
    stock_details = StockSerializer(source='stock', read_only=True)
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Alert
        fields = [
            'id', 'user', 'stock', 'alert_type', 'condition', 'target_price',
            'duration_minutes', 'status', 'is_active', 'created_at', 'updated_at',
            'last_checked', 'condition_start_time', 'stock_details', 'user_details'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_checked', 'condition_start_time']
    
    def validate(self, data):
        """Custom validation for alert data"""
        # Validate duration for duration alerts
        if data.get('alert_type') == 'duration' and data.get('duration_minutes', 0) <= 0:
            raise serializers.ValidationError("Duration alerts must have duration_minutes > 0")
        
        # Validate target price is positive
        if data.get('target_price', 0) <= 0:
            raise serializers.ValidationError("Target price must be positive")
        
        return data
    
    def create(self, validated_data):
        """Create alert and set user automatically"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

class AlertHistorySerializer(serializers.ModelSerializer):
    alert_details = AlertSerializer(source='alert', read_only=True)
    
    class Meta:
        model = AlertHistory
        fields = [
            'id', 'alert', 'triggered_at', 'stock_price', 'message',
            'notification_sent', 'notification_sent_at', 'alert_details'
        ]
        read_only_fields = ['id', 'triggered_at', 'stock_price', 'message', 'notification_sent', 'notification_sent_at']

class AlertCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating alerts"""
    class Meta:
        model = Alert
        fields = ['id', 'stock', 'alert_type', 'condition', 'target_price', 'duration_minutes', 'status', 'is_active', 'created_at']
        read_only_fields = ['id', 'status', 'is_active', 'created_at']
    
    def validate(self, data):
        """Custom validation for alert creation"""
        # Validate duration for duration alerts
        if data.get('alert_type') == 'duration' and data.get('duration_minutes', 0) <= 0:
            raise serializers.ValidationError("Duration alerts must have duration_minutes > 0")
        
        # Validate target price is positive
        if data.get('target_price', 0) <= 0:
            raise serializers.ValidationError("Target price must be positive")
        
        return data

class AlertUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating alerts"""
    class Meta:
        model = Alert
        fields = ['condition', 'target_price', 'duration_minutes', 'is_active']
    
    def validate(self, data):
        """Custom validation for alert updates"""
        # Validate duration for duration alerts
        if self.instance.alert_type == 'duration' and data.get('duration_minutes', 0) <= 0:
            raise serializers.ValidationError("Duration alerts must have duration_minutes > 0")
        
        # Validate target price is positive
        if data.get('target_price', 0) <= 0:
            raise serializers.ValidationError("Target price must be positive")
        
        return data
