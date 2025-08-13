from django.db import models
from django.contrib.auth.models import User
from stocks.models import Stock

class Alert(models.Model):
    ALERT_TYPES = [
        ('threshold', 'Threshold Alert'),
        ('duration', 'Duration Alert'),
    ]
    
    CONDITIONS = [
        ('above', 'Above'),
        ('below', 'Below'),
        ('equals', 'Equals'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('triggered', 'Triggered'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='alerts')
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    condition = models.CharField(max_length=10, choices=CONDITIONS)
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # For duration alerts
    duration_minutes = models.IntegerField(default=0, help_text="Duration in minutes for duration alerts", blank=True, null=True)
    
    # Alert status and metadata
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_checked = models.DateTimeField(null=True, blank=True)
    
    # For duration alerts - track when condition started
    condition_start_time = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Alert"
        verbose_name_plural = "Alerts"
    
    def __str__(self):
        return f"{self.user.username} - {self.stock.symbol} {self.condition} {self.target_price}"
    
    @property
    def description(self):
        if self.alert_type == 'threshold':
            return f"Alert when {self.stock.symbol} goes {self.condition} ${self.target_price}"
        else:
            return f"Alert when {self.stock.symbol} stays {self.condition} ${self.target_price} for {self.duration_minutes} minutes"

class AlertHistory(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE, related_name='history')
    triggered_at = models.DateTimeField(auto_now_add=True)
    stock_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    notification_sent = models.BooleanField(default=False)
    notification_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-triggered_at']
        verbose_name = "Alert History"
        verbose_name_plural = "Alert History"
    
    def __str__(self):
        return f"{self.alert.stock.symbol} - {self.triggered_at.strftime('%Y-%m-%d %H:%M')}"
