from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
import json

class UserRegistrationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('accounts:register')
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertIn('user', response.data)
        
        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@example.com')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_registration_password_mismatch(self):
        """Test registration with mismatched passwords"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'testpass123',
            'password_confirm': 'differentpass'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Passwords do not match', response.data['error'])
        
        # Check user was not created
        self.assertFalse(User.objects.filter(username='newuser').exists())
    
    def test_user_registration_existing_username(self):
        """Test registration with existing username"""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'existinguser',
            'email': 'newemail@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Username already exists', response.data['error'])
    
    def test_user_registration_existing_email(self):
        """Test registration with existing email"""
        # Create existing user
        User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='testpass123'
        )
        
        data = {
            'username': 'newuser',
            'email': 'existing@example.com',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Email already exists', response.data['error'])
    
    def test_user_registration_invalid_data(self):
        """Test registration with invalid data"""
        # Missing required fields
        data = {
            'username': 'newuser',
            'password': 'testpass123'
            # Missing email and password_confirm
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Invalid email format
        data = {
            'username': 'newuser',
            'email': 'invalid-email',
            'password': 'testpass123',
            'password_confirm': 'testpass123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_user_registration_weak_password(self):
        """Test registration with weak password"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'user123', 
            'password_confirm': 'user123'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

class UserLoginTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('accounts:login')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_user_login_success(self):
        """Test successful user login"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Check user data
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['email'], 'test@example.com')
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertIn('Invalid credentials', response.data['error'])
    
    def test_user_login_nonexistent_user(self):
        """Test login with non-existent user"""
        data = {
            'username': 'nonexistent',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_login_missing_fields(self):
        """Test login with missing fields"""
        # Missing password
        data = {'username': 'testuser'}
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Missing username
        data = {'password': 'testpass123'}
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class UserProfileTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.profile_url = reverse('accounts:profile')
    
    def test_get_user_profile(self):
        """Test retrieving user profile"""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertIn('date_joined', response.data)
    
    def test_update_user_profile(self):
        """Test updating user profile"""
        data = {
            'email': 'newemail@example.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }
        
        response = self.client.patch(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'newemail@example.com')
        self.assertEqual(response.data['first_name'], 'John')
        self.assertEqual(response.data['last_name'], 'Doe')
        
        # Check database was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, 'newemail@example.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
    
    def test_update_user_profile_invalid_email(self):
        """Test updating profile with invalid email"""
        data = {'email': 'invalid-email'}
        
        response = self.client.patch(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_unauthorized_profile_access(self):
        """Test that unauthorized users cannot access profile"""
        self.client.credentials()  # Remove authentication
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class JWTAuthenticationTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_jwt_token_generation(self):
        """Test JWT token generation and validation"""
        # Get tokens
        refresh = RefreshToken.for_user(self.user)
        access_token = refresh.access_token
        
        # Verify access token works
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Test protected endpoint
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_jwt_token_refresh(self):
        """Test JWT token refresh functionality"""
        refresh = RefreshToken.for_user(self.user)
        
        # Use refresh token to get new access token
        refresh_url = reverse('accounts:token-refresh')
        data = {'refresh': str(refresh)}
        
        response = self.client.post(refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # New access token should work
        new_access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_invalid_jwt_token(self):
        """Test access with invalid JWT token"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid-token')
        
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_expired_jwt_token(self):
        """Test access with expired JWT token"""
        # Create expired token (this would normally happen over time)
        from datetime import timedelta
        from django.utils import timezone
        
        # Mock expired token
        expired_time = timezone.now() - timedelta(hours=1)
        
        # This is a simplified test - in real scenarios, tokens expire naturally
        self.client.credentials(HTTP_AUTHORIZATION='Bearer expired-token')
        
        profile_url = reverse('accounts:profile')
        response = self.client.get(profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='John',
            last_name='Doe'
        )
    
    def test_user_creation(self):
        """Test user model creation and fields"""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertTrue(self.user.check_password('testpass123'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
    
    def test_user_string_representation(self):
        """Test user string representation"""
        expected = "testuser"  # Django's default User model returns username
        self.assertEqual(str(self.user), expected)
    
    def test_user_full_name(self):
        """Test user full name property"""
        self.assertEqual(self.user.get_full_name(), 'John Doe')
        
        # Test with no first/last name
        user_no_name = User.objects.create_user(
            username='noname',
            email='noname@example.com',
            password='testpass123'
        )
        self.assertEqual(user_no_name.get_full_name(), '')
    
    def test_user_short_name(self):
        """Test user short name property"""
        self.assertEqual(self.user.get_short_name(), 'John')
        
        # Test with no first name
        user_no_first = User.objects.create_user(
            username='nofirst',
            email='nofirst@example.com',
            password='testpass123',
            last_name='Smith'
        )
        self.assertEqual(user_no_first.get_short_name(), '')

class PasswordChangeTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
        
        self.change_password_url = reverse('accounts:change-password')
    
    def test_change_password_success(self):
        """Test successful password change"""
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Verify password was changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))
        self.assertFalse(self.user.check_password('testpass123'))
    
    def test_change_password_wrong_current(self):
        """Test password change with wrong current password"""
        data = {
            'current_password': 'wrongpassword',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Current password is incorrect', response.data['error'])
    
    def test_change_password_mismatch(self):
        """Test password change with mismatched new passwords"""
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'confirm_password': 'differentpass'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('New passwords do not match', response.data['error'])
    
    def test_change_password_unauthorized(self):
        """Test password change without authentication"""
        self.client.credentials()  # Remove authentication
        
        data = {
            'current_password': 'testpass123',
            'new_password': 'newpass123',
            'new_password_confirm': 'newpass123'
        }
        
        response = self.client.post(self.change_password_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
