from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from decimal import Decimal
from unittest.mock import patch, MagicMock
import json

from .models import Stock, StockPrice
from .services import (
    fetch_stock_price, check_rate_limit, validate_stock_symbol, 
    get_api_status, get_cached_stock_price
)
# from .tasks import update_single_stock_price, initialize_stocks
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()

class StockModelTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            price=Decimal('150.00'),
            exchange='NASDAQ',
            currency='USD'
        )
    
    def test_stock_creation(self):
        """Test stock model creation and fields"""
        self.assertEqual(self.stock.symbol, 'AAPL')
        self.assertEqual(self.stock.name, 'Apple Inc.')
        self.assertEqual(self.stock.price, Decimal('150.00'))
        self.assertEqual(self.stock.exchange, 'NASDAQ')
        self.assertEqual(self.stock.currency, 'USD')
        self.assertTrue(self.stock.is_active)
        self.assertIsNotNone(self.stock.created_at)
        self.assertIsNotNone(self.stock.last_updated)
    
    def test_stock_string_representation(self):
        """Test stock string representation"""
        expected = "AAPL - $150.00"
        self.assertEqual(str(self.stock), expected)
    
    def test_stock_price_history(self):
        """Test stock price history tracking"""
        # Create price history records with different timestamps
        from django.utils import timezone
        from datetime import timedelta
        
        # Create first price record
        first_price = StockPrice.objects.create(
            stock=self.stock,
            price=Decimal('150.00')
        )
        
        # Manually set timestamp to ensure ordering
        first_price.timestamp = timezone.now() - timedelta(minutes=1)
        first_price.save()
        
        # Create second price record (will have current timestamp)
        StockPrice.objects.create(
            stock=self.stock,
            price=Decimal('155.00')
        )
        
        self.assertEqual(self.stock.price_history.count(), 2)
        self.assertEqual(self.stock.price_history.first().price, Decimal('155.00'))
    
    def test_stock_ordering(self):
        """Test stock ordering by symbol"""
        Stock.objects.create(symbol='GOOGL', name='Google')
        Stock.objects.create(symbol='MSFT', name='Microsoft')
        
        stocks = Stock.objects.all()
        self.assertEqual(stocks[0].symbol, 'AAPL')
        self.assertEqual(stocks[1].symbol, 'GOOGL')
        self.assertEqual(stocks[2].symbol, 'MSFT')

class StockPriceModelTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            price=Decimal('150.00')
        )
    
    def test_stock_price_creation(self):
        """Test stock price history creation"""
        price_record = StockPrice.objects.create(
            stock=self.stock,
            price=Decimal('155.00')
        )
        
        self.assertEqual(price_record.stock, self.stock)
        self.assertEqual(price_record.price, Decimal('155.00'))
        self.assertIsNotNone(price_record.timestamp)
    
    def test_stock_price_ordering(self):
        """Test stock price ordering by timestamp"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Create first price record with older timestamp
        first_price = StockPrice.objects.create(
            stock=self.stock,
            price=Decimal('150.00')
        )
        first_price.timestamp = timezone.now() - timedelta(minutes=5)
        first_price.save()
        
        # Create second price record with current timestamp
        second_price = StockPrice.objects.create(
            stock=self.stock,
            price=Decimal('155.00')
        )
        second_price.timestamp = timezone.now()
        second_price.save()
        
        prices = StockPrice.objects.all()
        self.assertEqual(prices[0].price, Decimal('155.00'))  # Most recent first
        self.assertEqual(prices[1].price, Decimal('150.00'))

class StockServicesTest(TestCase):
    def setUp(self):
        # Mock cache for testing
        cache.clear()
    
    def test_validate_stock_symbol(self):
        """Test stock symbol validation"""
        # Valid symbols
        self.assertTrue(validate_stock_symbol('AAPL')[0])
        self.assertTrue(validate_stock_symbol('GOOGL')[0])
        self.assertTrue(validate_stock_symbol('BRK.A')[0])
        self.assertTrue(validate_stock_symbol('MSFT')[0])
        
        # Invalid symbols
        self.assertFalse(validate_stock_symbol('')[0])
        self.assertFalse(validate_stock_symbol('A' * 11)[0])  # Too long
        self.assertFalse(validate_stock_symbol('AAP@L')[0])   # Invalid chars
        self.assertFalse(validate_stock_symbol('123')[0])     # Numbers only
    
    def test_check_rate_limit(self):
        """Test API rate limiting"""
        
        # Should allow first 100 calls
        for i in range(100):
            self.assertTrue(check_rate_limit())
        
        # 101st call should be blocked
        self.assertFalse(check_rate_limit())
        
        # Wait for cache to expire (simulate)
        cache.delete('twelve_data_api_calls')
        
        # Should allow calls again
        self.assertTrue(check_rate_limit())
    
    def test_get_api_status(self):
        """Test API status information"""
        status_info = get_api_status()
        
        self.assertIn('api_key_configured', status_info)
        self.assertIn('rate_limit_remaining', status_info)
        self.assertIn('rate_limit_max', status_info)
        self.assertIn('rate_limit_reset_seconds', status_info)
        
        self.assertEqual(status_info['rate_limit_max'], 100)
    
    @patch('stocks.services.requests.get')
    def test_fetch_stock_price_success(self, mock_get):
        """Test successful stock price fetching"""
        # Mock successful API response
        mock_response = MagicMock()
        mock_response.json.return_value = {'price': '150.50'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock rate limit check
        with patch('stocks.services.check_rate_limit', return_value=True):
            price = fetch_stock_price('AAPL')
            
        self.assertEqual(price, Decimal('150.50'))
    
    @patch('stocks.services.requests.get')
    def test_fetch_stock_price_api_error(self, mock_get):
        """Test API error handling"""
        # Mock API error response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'error',
            'message': 'API key invalid'
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock rate limit check
        with patch('stocks.services.check_rate_limit', return_value=True):
            with self.assertRaises(Exception) as context:
                fetch_stock_price('AAPL')
            
            self.assertIn('API error: API key invalid', str(context.exception))
    
    @patch('stocks.services.requests.get')
    def test_fetch_stock_price_timeout(self, mock_get):
        """Test timeout error handling"""
        # Mock timeout error
        mock_get.side_effect = Exception('Request timeout')
        
        # Mock rate limit check
        with patch('stocks.services.check_rate_limit', return_value=True):
            with self.assertRaises(Exception) as context:
                fetch_stock_price('AAPL')
            
            self.assertIn('Request timeout', str(context.exception))

class StockAPITest(APITestCase):
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
    
    def test_list_stocks(self):
        """Test listing stocks via API"""
        url = reverse('stocks:stock-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['symbol'], 'AAPL')
    
    def test_stock_detail(self):
        """Test retrieving specific stock details"""
        url = reverse('stocks:stock-detail', args=[self.stock.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['symbol'], 'AAPL')
        self.assertEqual(response.data['name'], 'Apple Inc.')
    
    def test_update_stock_price(self):
        """Test updating stock price via API"""
        url = reverse('stocks:update-price')
        data = {'symbol': 'AAPL'}
        
        # Mock the service function instead of the task
        with patch('stocks.views.update_single_stock_price') as mock_service:
            mock_service.return_value = 'Price updated successfully for AAPL'
            
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_service.assert_called_once_with('AAPL')
    
    def test_update_stock_price_invalid_symbol(self):
        """Test updating stock price with invalid symbol"""
        url = reverse('stocks:update-price')
        data = {'symbol': 'AAP@L'}  # Invalid symbol with special character
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_unauthorized_access(self):
        """Test that unauthorized users cannot access stocks"""
        self.client.credentials()  # Remove authentication
        
        url = reverse('stocks:stock-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class StockTasksTest(TestCase):
    def setUp(self):
        self.stock = Stock.objects.create(
            symbol='AAPL',
            name='Apple Inc.',
            price=Decimal('150.00')
        )
    
    
    def test_placeholder(self):
        """Placeholder test to ensure the class can run"""
        self.assertTrue(True)

class StockEdgeCaseTest(TestCase):
    def test_stock_with_no_price(self):
        """Test stock model behavior with no price"""
        stock = Stock.objects.create(
            symbol='NEW',
            name='New Company'
        )
        
        self.assertIsNone(stock.price)
        self.assertEqual(str(stock), 'NEW - None')
    
    def test_stock_price_decimal_precision(self):
        """Test stock price decimal precision handling"""
        stock = Stock.objects.create(
            symbol='PRECISE',
            name='Precise Company',
            price=Decimal('123.45')
        )
        
        # Should handle 2 decimal places
        self.assertEqual(stock.price, Decimal('123.45'))
        
        # Create price history with 2 decimal places
        StockPrice.objects.create(
            stock=stock,
            price=Decimal('123.45')
        )
        
        self.assertEqual(stock.price_history.first().price, Decimal('123.45'))
    
    def test_stock_symbol_case_sensitivity(self):
        """Test stock symbol case handling"""
        # Create with lowercase
        stock_lower = Stock.objects.create(
            symbol='aapl',
            name='Apple Lower'
        )
        
        # Create with uppercase
        stock_upper = Stock.objects.create(
            symbol='AAPL',
            name='Apple Upper'
        )
        
        # Should be treated as different symbols
        self.assertNotEqual(stock_lower.id, stock_upper.id)
        self.assertEqual(stock_lower.symbol, 'aapl')
        self.assertEqual(stock_upper.symbol, 'AAPL')
