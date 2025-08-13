from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from datetime import timedelta
import json

from .models import Alert, AlertHistory
from stocks.models import Stock
from .services import check_alert_condition, check_threshold_condition, check_duration_condition

class AlertModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            price=Decimal('150.00')
        )
    
    def test_alert_creation(self):
        """Test creating different types of alerts"""
        # Threshold alert
        threshold_alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        self.assertEqual(threshold_alert.alert_type, 'threshold')
        self.assertEqual(threshold_alert.condition, 'above')
        self.assertEqual(threshold_alert.status, 'active')
        self.assertTrue(threshold_alert.is_active)
        
        # Duration alert
        duration_alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='duration',
            condition='below',
            target_price=Decimal('100.00'),
            duration_minutes=120
        )
        self.assertEqual(duration_alert.alert_type, 'duration')
        self.assertEqual(duration_alert.duration_minutes, 120)
    
    def test_alert_description(self):
        """Test alert description property"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        expected = "Alert when AAPL goes above $200.00"
        self.assertEqual(alert.description, expected)
        
        # Duration alert
        duration_alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='duration',
            condition='below',
            target_price=Decimal('100.00'),
            duration_minutes=120
        )
        expected = "Alert when AAPL stays below $100.00 for 120 minutes"
        self.assertEqual(duration_alert.description, expected)
    
    def test_alert_history(self):
        """Test alert history creation"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        
        history = AlertHistory.objects.create(
            alert=alert,
            stock_price=Decimal('210.00'),
            message='Test alert triggered'
        )
        
        self.assertEqual(history.stock_price, Decimal('210.00'))
        self.assertEqual(history.alert, alert)
        self.assertFalse(history.notification_sent)

class AlertConditionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            price=Decimal('150.00')
        )
    
    def test_threshold_condition_above(self):
        """Test above threshold condition"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('100.00')
        )
        
        # Current price (150) > target (100) = True
        self.assertTrue(check_threshold_condition(alert, Decimal('150.00'), Decimal('100.00')))
        
        # Current price (50) < target (100) = False
        self.assertFalse(check_threshold_condition(alert, Decimal('50.00'), Decimal('100.00')))
    
    def test_threshold_condition_below(self):
        """Test below threshold condition"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='below',
            target_price=Decimal('200.00')
        )
        
        # Current price (150) < target (200) = True
        self.assertTrue(check_threshold_condition(alert, Decimal('150.00'), Decimal('200.00')))
        
        # Current price (250) > target (200) = False
        self.assertFalse(check_threshold_condition(alert, Decimal('250.00'), Decimal('200.00')))
    
    def test_threshold_condition_equals(self):
        """Test equals threshold condition"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='equals',
            target_price=Decimal('150.00')
        )
        
        # Current price (150) = target (150) = True
        self.assertTrue(check_threshold_condition(alert, Decimal('150.00'), Decimal('150.00')))
        
        # Current price (150.01) ≈ target (150) = True (within tolerance)
        self.assertTrue(check_threshold_condition(alert, Decimal('150.01'), Decimal('150.00')))
        
        # Current price (160) ≠ target (150) = False
        self.assertFalse(check_threshold_condition(alert, Decimal('160.00'), Decimal('150.00')))
    
    def test_duration_condition(self):
        """Test duration condition logic"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='duration',
            condition='below',
            target_price=Decimal('200.00'),
            duration_minutes=60
        )
        
        # Initially, condition not met
        self.assertFalse(check_duration_condition(alert, Decimal('250.00'), Decimal('200.00')))
        
        # Condition met, start timing
        self.assertFalse(check_duration_condition(alert, Decimal('150.00'), Decimal('200.00')))
        
        # Simulate time passing
        alert.condition_start_time = timezone.now() - timedelta(minutes=30)
        alert.save()
        
        # Condition met but duration not reached
        self.assertFalse(check_duration_condition(alert, Decimal('150.00'), Decimal('200.00')))
        
        # Duration reached
        alert.condition_start_time = timezone.now() - timedelta(minutes=70)
        alert.save()
        
        self.assertTrue(check_duration_condition(alert, Decimal('150.00'), Decimal('200.00')))

class AlertAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            price=Decimal('150.00')
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_create_alert(self):
        """Test creating a new alert via API"""
        url = reverse('alerts:alert-list')
        data = {
            'stock': self.stock.id,
            'alert_type': 'threshold',
            'condition': 'above',
            'target_price': '200.00'
        }
        
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        alert = Alert.objects.get(id=response.data['id'])
        self.assertEqual(alert.user, self.user)
        self.assertEqual(alert.stock, self.stock)
        self.assertEqual(alert.alert_type, 'threshold')
    
    def test_list_user_alerts(self):
        """Test listing alerts for authenticated user"""
        # Create alerts for this user
        Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        
        # Create alert for different user
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='testpass123'
        )
        Alert.objects.create(
            user=other_user,
            stock=self.stock,
            alert_type='threshold',
            condition='below',
            target_price=Decimal('100.00')
        )
        
        url = reverse('alerts:alert-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only user's alerts
        self.assertEqual(response.data[0]['stock'], self.stock.id)
    
    def test_alert_detail(self):
        """Test retrieving specific alert details"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        
        url = reverse('alerts:alert-detail', args=[alert.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], alert.id)
        self.assertEqual(response.data['stock'], self.stock.id)
    
    def test_update_alert(self):
        """Test updating an alert"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        
        url = reverse('alerts:alert-detail', args=[alert.id])
        data = {'target_price': '250.00'}
        
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        alert.refresh_from_db()
        self.assertEqual(alert.target_price, Decimal('250.00'))
    
    def test_delete_alert(self):
        """Test deleting an alert"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        
        url = reverse('alerts:alert-detail', args=[alert.id])
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Alert.objects.filter(id=alert.id).exists())
    
    def test_toggle_alert_active(self):
        """Test toggling alert active status"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        
        url = reverse('alerts:alert-toggle-active', args=[alert.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])
        
        # Toggle again
        response = self.client.post(url)
        self.assertTrue(response.data['is_active'])
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access alerts"""
        self.client.credentials()  # Remove authentication
        
        url = reverse('alerts:alert-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_alert_history_api(self):
        """Test alert history API endpoints"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        
        # Create some history
        AlertHistory.objects.create(
            alert=alert,
            stock_price=Decimal('210.00'),
            message='Test alert triggered'
        )
        
        url = reverse('alerts:alert-history-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['stock_price'], '210.00')

class AlertEdgeCaseTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            price=Decimal('150.00')
        )
    
    def test_alert_with_no_stock_price(self):
        """Test alert condition check when stock has no price"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('200.00')
        )
        
        # Remove stock price
        self.stock.price = None
        self.stock.save()
        
        # Should return False when no price available
        self.assertFalse(check_alert_condition(alert))
    
    def test_duration_alert_reset(self):
        """Test duration alert resets when condition is no longer met"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='duration',
            condition='below',
            target_price=Decimal('200.00'),
            duration_minutes=60
        )
        
        # Start timing
        alert.condition_start_time = timezone.now() - timedelta(minutes=30)
        alert.save()
        
        # Condition no longer met - should reset timing
        self.assertFalse(check_duration_condition(alert, Decimal('250.00'), Decimal('200.00')))
        
        alert.refresh_from_db()
        self.assertIsNone(alert.condition_start_time)
    
    def test_alert_status_transitions(self):
        """Test alert status transitions"""
        alert = Alert.objects.create(
            user=self.user,
            stock=self.stock,
            alert_type='threshold',
            condition='above',
            target_price=Decimal('100.00')  # Current price 150 > 100
        )
        
        # Initially active
        self.assertEqual(alert.status, 'active')
        
    
        alert.status = 'triggered'
        alert.save()
        
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'triggered')
        
        alert.status = 'active'
        alert.save()
        
        alert.refresh_from_db()
        self.assertEqual(alert.status, 'active')
