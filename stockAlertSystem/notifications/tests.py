from django.core.management import execute_from_command_line
from django.test import TestCase
from django.contrib.auth.models import User
from stocks.models import Stock
from alerts.models import Alert, AlertHistory
from notifications.services import send_email_notification
import logging

class EmailNotificationTests(TestCase):
    """Test cases for email notification functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',  # Change this to your email
            first_name='Test',
            last_name='User',
            password='testpass123'
        )
        
        self.stock = Stock.objects.create(
            symbol='TEST',
            name='Test Stock',
            price=100.00,
            is_active=True
        )
    
    def test_email_configuration(self):
        """Test if email configuration is properly set up"""
        from django.conf import settings
        
        print("=== Email Configuration Test ===")
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_HOST_USER: {'***' if settings.EMAIL_HOST_USER else 'NOT SET'}")
        print(f"EMAIL_HOST_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
        
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("Email credentials are not configured")
            self.fail("Email credentials are not configured")
        
        print("Email configuration appears to be set up")
    
    def test_direct_email(self):
        """Test direct email sending without alerts"""
        print("\n=== Testing Direct Email ===")
        
        try:
            # Test direct email (call function directly in tests)
            result = send_email_notification(
                user_id=self.user.id,
                subject="Test Email - Stock Alert System",
                message="This is a test email from the stock alert system. If you receive this, email notifications are working correctly!"
            )
            
            print(f"Email sent successfully: {result}")
            print("Check your email in a few moments...")
            
        except Exception as e:
            print(f"Error sending test email: {e}")
            self.fail(f"Error sending test email: {e}")
    
    def test_alert_notification(self):
        """Test complete alert notification flow"""
        print("\n=== Testing Alert Notification Flow ===")
        
        try:
            # Create test alert
            alert = Alert.objects.create(
                user=self.user,
                stock=self.stock,
                alert_type='threshold',
                condition='above',
                target_price=105.00,
                is_active=True
            )
            
            # Create alert history (simulating triggered alert)
            alert_history = AlertHistory.objects.create(
                alert=alert,
                stock_price=110.00,
                message="Price $110.00 above threshold $105.00"
            )
            
            # Test alert notification
            from alerts.services import send_alert_notification
            send_alert_notification(alert, alert_history)
            
            print("Alert notification test completed")
            print("Check your email for the alert notification...")
            
        except Exception as e:
            print(f"Error testing alert notification: {e}")
            self.fail(f"Error testing alert notification: {e}")
    
    def test_user_creation(self):
        """Test that test user was created successfully"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
    
    def test_stock_creation(self):
        """Test that test stock was created successfully"""
        self.assertEqual(self.stock.symbol, 'TEST')
        self.assertEqual(self.stock.name, 'Test Stock')
        self.assertEqual(float(self.stock.price), 100.00)

# Standalone test runner for development
def run_standalone_tests():
    """Run tests outside of Django test framework"""
    import os
    import django
    import sys
    
    # Add the project to the Python path
    sys.path.insert(0, 'stockAlertSystem')
    
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockAlertSystem.settings')
    django.setup()
    
    def test_email_configuration():
        """Test if email configuration is properly set up"""
        from django.conf import settings
        
        print("=== Email Configuration Test ===")
        print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
        print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
        print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
        print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
        print(f"EMAIL_HOST_USER: {'***' if settings.EMAIL_HOST_USER else 'NOT SET'}")
        print(f"EMAIL_HOST_PASSWORD: {'***' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
        
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            print("Email credentials are not configured")
            return False
        
        print("Email configuration appears to be set up")
        return True
    
    def create_test_user_and_stock():
        """Create test user and stock for testing"""
        print("\n=== Creating Test Data ===")
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',  # Change this to your email
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            print(f"Created test user: {user.username}")
        else:
            print(f"Using existing test user: {user.username}")
        
        # Create test stock
        stock, created = Stock.objects.get_or_create(
            symbol='TEST',
            defaults={
                'name': 'Test Stock',
                'price': 100.00,
                'is_active': True
            }
        )
        
        if created:
            print(f"Created test stock: {stock.symbol}")
        else:
            print(f"Using existing test stock: {stock.symbol}")
        
        return user, stock
    
    def test_direct_email():
        """Test direct email sending without alerts"""
        print("\n=== Testing Direct Email ===")
        
        try:
            # Create test user
            user, _ = create_test_user_and_stock()
            
            # Test direct email
            result = send_email_notification.delay(
                user_id=user.id,
                subject="Test Email - Stock Alert System",
                message="This is a test email from the stock alert system. If you receive this, email notifications are working correctly!"
            )
            
            print(f"Email task queued: {result}")
            print("Check your email in a few moments...")
            return True
            
        except Exception as e:
            print(f"Error sending test email: {e}")
            return False
    
    def test_alert_notification():
        """Test complete alert notification flow"""
        print("\n=== Testing Alert Notification Flow ===")
        
        try:
            user, stock = create_test_user_and_stock()
            
            # Create test alert
            alert = Alert.objects.create(
                user=user,
                stock=stock,
                alert_type='threshold',
                condition='above',
                target_price=105.00,
                is_active=True
            )
            
            # Create alert history (simulating triggered alert)
            alert_history = AlertHistory.objects.create(
                alert=alert,
                stock_price=110.00,
                message="Price $110.00 above threshold $105.00"
            )
            
            # Test alert notification
            from alerts.services import send_alert_notification
            send_alert_notification(alert, alert_history)
            
            print("Alert notification test completed")
            print("Check your email for the alert notification...")
            return True
            
        except Exception as e:
            print(f"Error testing alert notification: {e}")
            return False
    
    def run_all_tests():
        """Run all email notification tests"""
        print("Starting Email Notification Tests\n")
        
        # Test 1: Email configuration
        if not test_email_configuration():
            print("\n Please configure your email settings in .env file")
            return
        
        # Test 2: Direct email
        test_direct_email()
        
        # Test 3: Alert notification flow
        test_alert_notification()
        
        print("\n All tests completed! Check your email for test messages.")
