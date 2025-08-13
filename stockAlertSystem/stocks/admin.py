from django.contrib import admin
from .models import Stock, StockPrice

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'price', 'currency', 'exchange', 'is_active', 'last_updated']
    list_filter = ['currency', 'exchange', 'is_active', 'last_updated']
    search_fields = ['symbol', 'name']
    readonly_fields = ['last_updated', 'created_at']
    list_editable = ['is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('symbol', 'name', 'price')
        }),
        ('Market Information', {
            'fields': ('currency', 'exchange', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ['stock', 'price', 'timestamp']
    list_filter = ['stock', 'timestamp']
    search_fields = ['stock__symbol', 'stock__name']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
