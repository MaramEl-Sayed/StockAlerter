from rest_framework import serializers
from .models import Stock, StockPrice

class StockPriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockPrice
        fields = ['id', 'price', 'timestamp']
        read_only_fields = ['id', 'timestamp']

class StockSerializer(serializers.ModelSerializer):
    price_history = StockPriceSerializer(many=True, read_only=True)
    current_price = serializers.DecimalField(source='price', max_digits=10, decimal_places=6, read_only=True)
    
    class Meta:
        model = Stock
        fields = [
            'id', 'symbol', 'name', 'current_price', 'last_updated', 'currency', 
            'exchange', 'is_active', 'created_at', 'price_history'
        ]
        read_only_fields = ['id', 'current_price', 'last_updated', 'created_at']

class StockCreateSerializer(serializers.ModelSerializer):
    """Simplified serializer for creating stocks"""
    class Meta:
        model = Stock
        fields = ['symbol', 'name', 'currency', 'exchange']

class StockUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating stocks"""
    class Meta:
        model = Stock
        fields = ['name', 'is_active']

class StockPriceUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating stock prices"""
    class Meta:
        model = Stock
        fields = ['price']
