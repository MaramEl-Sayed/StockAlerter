from django.contrib import admin
from .models import Alert, AlertHistory

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'stock', 'alert_type', 'condition', 'target_price', 
        'status', 'is_active', 'created_at'
    ]
    list_filter = [
        'alert_type', 'condition', 'status', 'is_active', 'created_at'
    ]
    search_fields = ['user__username', 'stock__symbol', 'stock__name']
    readonly_fields = ['created_at', 'updated_at', 'last_checked', 'condition_start_time']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'stock', 'alert_type', 'condition', 'target_price')
        }),
        ('Duration Settings', {
            'fields': ('duration_minutes',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_checked', 'condition_start_time'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_alerts', 'deactivate_alerts', 'reset_to_active']
    
    def activate_alerts(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} alerts activated.')
    activate_alerts.short_description = "Activate selected alerts"
    
    def deactivate_alerts(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} alerts deactivated.')
    deactivate_alerts.short_description = "Deactivate selected alerts"
    
    def reset_to_active(self, request, queryset):
        updated = queryset.update(status='active', condition_start_time=None)
        self.message_user(request, f'{updated} alerts reset to active status.')
    reset_to_active.short_description = "Reset alerts to active status"

@admin.register(AlertHistory)
class AlertHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'alert', 'stock_symbol', 'stock_price', 'triggered_at', 
        'notification_sent'
    ]
    list_filter = ['triggered_at', 'notification_sent']
    search_fields = ['alert__user__username', 'alert__stock__symbol']
    readonly_fields = ['triggered_at', 'stock_price', 'message']
    
    def stock_symbol(self, obj):
        return obj.alert.stock.symbol
    stock_symbol.short_description = 'Stock Symbol'
    
    def has_add_permission(self, request):
        return False  # AlertHistory records are created automatically
    
    def has_change_permission(self, request, obj=None):
        return False  # AlertHistory records should not be modified
