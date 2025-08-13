#!/usr/bin/env python
"""
Real-world testing script for email notifications
Run this to create real alerts and trigger notifications
"""

import os
import django
import sys

# Add the project to the Python path
sys.path.insert(0, 'stockAlertSystem')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockAlertSystem.settings')
django.setup()

from django.contrib.auth.models import User
from stocks.models import Stock
from alerts.models import Alert, AlertHistory
from alerts.services import check_all_alerts, send_alert_notification
from stocks.services import update_all_stock_prices
from django.utils import timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_real_test():
    """Set up real test with actual stocks and user"""
    print("=== Setting Up Real Alert Test ===")
    
    # Get current logged-in user (you)
    try:
        user = User.objects.first()
        if not user:
            print("No users found. Please create a user first.")
            return None, None
        
        print(f"Using user: {user.username} ({user.email})")
        
        # Get real stocks
        stocks = Stock.objects.filter(is_active=True)[:5]
        if not stocks:
            print("No active stocks found. Please run stock initialization first.")
            return None, None
            
        print(f"Found {len(stocks)} active stocks")
        for stock in stocks:
            print(f"   - {stock.symbol}: ${stock.price}")
        
        return user, stocks
        
    except Exception as e:
        print(f"Error setting up test: {e}")
        return None, None

def create_real_alert(user, stock):
    """Create a real alert that will trigger soon"""
    print("\n=== Creating Real Alert ===")
    
    try:
        # Create alert slightly below current price to trigger
        target_price = float(stock.price) * 0.95  # 5% below current price
        
        alert = Alert.objects.create(
            user=user,
            stock=stock,
            alert_type='threshold',
            condition='below',
            target_price=target_price,
            is_active=True
        )
        
        print(f"   Created alert #{alert.id}")
        print(f"   Stock: {stock.symbol}")
        print(f"   Current Price: ${stock.price}")
        print(f"   Alert Condition: Price goes below ${target_price}")
        print(f"   This alert will trigger when price drops 5%")
        
        return alert
        
    except Exception as e:
        print(f"Error creating alert: {e}")
        return None

def trigger_alert_manually(alert):
    """Manually trigger the alert for testing"""
    print("\n=== Manually Triggering Alert ===")
    
    try:
        # Create alert history record (simulating triggered alert)
        alert_history = AlertHistory.objects.create(
            alert=alert,
            stock_price=alert.target_price - 1,  # Price below target
            message=f"Price ${alert.target_price - 1} below threshold ${alert.target_price}"
        )
        
        # Send notification
        send_alert_notification(alert, alert_history)
        
        print("Alert triggered and notification sent!")
        print("Check your email for the notification...")
        
        return True
        
    except Exception as e:
        print(f"Error triggering alert: {e}")
        return False

def test_with_existing_alerts():
    """Test with existing active alerts"""
    print("\n=== Testing with Existing Alerts ===")
    
    try:
        active_alerts = Alert.objects.filter(is_active=True)
        
        if not active_alerts:
            print("No active alerts found")
            return False
            
        print(f"Found {len(active_alerts)} active alerts")
        
        # Update stock prices to potentially trigger alerts
        print("Updating stock prices...")
        update_all_stock_prices()
        
        # Check all alerts
        print("Checking alerts...")
        result = check_all_alerts()
        
        if result and result['triggered_count'] > 0:
            print(f"{result['triggered_count']} alerts triggered!")
            print("Check your email for notifications...")
        else:
            print("No alerts triggered yet. Try creating new alerts closer to current prices.")
            
        return True
        
    except Exception as e:
        print(f"Error testing existing alerts: {e}")
        return False

def run_real_test():
    """Run complete real-world test"""
    print("Starting Real Alert Testing\n")
    
    # Setup
    user, stocks = setup_real_test()
    if not user or not stocks:
        return
    
    # Option 1: Create new alert
    print("\n--- Option 1: Create New Alert ---")
    stock = stocks[0]  # Use first available stock
    alert = create_real_alert(user, stock)
    if alert:
        trigger_alert_manually(alert)
    
    # Option 2: Test existing alerts
    print("\n--- Option 2: Test Existing Alerts ---")
    test_with_existing_alerts()
    
    print("\n Real alert testing completed!")
    print("Check your email for notifications!")

if __name__ == "__main__":
    run_real_test()
