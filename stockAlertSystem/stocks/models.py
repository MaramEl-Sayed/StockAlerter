from django.db import models
from django.utils import timezone

class Stock(models.Model):
    symbol = models.CharField(max_length=10, unique=True)  # e.g. AAPL
    name = models.CharField(max_length=100, blank=True)    # optional company name
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    # Additional fields for better stock information
    currency = models.CharField(max_length=3, default='USD')
    exchange = models.CharField(max_length=10, default='NASDAQ')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        if self.price is not None:
            return f"{self.symbol} - ${self.price}"
        else:
            return f"{self.symbol} - None"

    class Meta:
        ordering = ['symbol']
        verbose_name = "Stock"
        verbose_name_plural = "Stocks"

class StockPrice(models.Model):
    """Historical stock price data for duration alerts"""
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='price_history')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Stock Price"
        verbose_name_plural = "Stock Prices"
        # Index for efficient querying
        indexes = [
            models.Index(fields=['stock', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.stock.symbol} - ${self.price} at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
