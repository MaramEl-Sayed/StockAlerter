from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import update_session_auth_hash, authenticate
from .serializers import RegisterSerializer, UserProfileSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):
    def post(self, request):
        data = request.data
        
        # Check if passwords match
        password = data.get('password')
        password_confirm = data.get('password_confirm')
        
        if password != password_confirm:
            return Response({"error": "Passwords do not match"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if username already exists
        if User.objects.filter(username=data.get('username')).exists():
            return Response({"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if email already exists
        if User.objects.filter(email=data.get('email')).exists():
            return Response({"error": "Email already exists"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check password strength
        if len(password) < 8:
            return Response({"error": "Password must be at least 8 characters long"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for weak password patterns
        username = data.get('username', '').lower()
        email = data.get('email', '').lower()
        
        # Check if password contains username
        if username and username in password.lower():
            return Response({"error": "Password should not contain your username"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if password contains email username part
        email_username = email.split('@')[0] if '@' in email else ''
        if email_username and email_username in password.lower():
            return Response({"error": "Password should not contain your email address"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for common weak patterns
        weak_patterns = [
            'password', '123456', '123456789', 'qwerty', 'abc123', 'password123',
            'admin', 'letmein', 'welcome', 'monkey', 'dragon', 'master'
        ]
        
        password_lower = password.lower()
        for pattern in weak_patterns:
            if pattern in password_lower:
                return Response({"error": "Password is too weak. Please choose a stronger password"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for sequential characters
        sequential_patterns = [
            '123456789', '987654321', 'abcdefghijklmnopqrstuvwxyz',
            'zyxwvutsrqponmlkjihgfedcba', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm'
        ]
        
        for seq in sequential_patterns:
            if seq in password_lower:
                return Response({"error": "Password should not contain sequential characters"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for only numbers or only letters
        if password.isdigit():
            return Response({"error": "Password should not be only numbers"}, status=status.HTTP_400_BAD_REQUEST)
        
        if password.isalpha():
            return Response({"error": "Password should contain both letters and numbers"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "message": "User registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }, status=status.HTTP_201_CREATED)
        
        # Handle serializer validation errors
        errors = serializer.errors
        if 'email' in errors:
            return Response({"error": "Enter a valid email address."}, status=status.HTTP_400_BAD_REQUEST)
        elif 'username' in errors:
            return Response({"error": "Username is required."}, status=status.HTTP_400_BAD_REQUEST)
        elif 'password' in errors:
            return Response({"error": "Password is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)

class CustomLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is None:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined
            }
        }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": f"Hello, {request.user.username}. This is a protected route."})

class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Return user data instead of profile data
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined
        })
    
    def patch(self, request):
        # Update user data
        user = request.user
        data = request.data
        
        # Validate email if provided
        if 'email' in data:
            if '@' not in data['email']:
                return Response({'error': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update user fields
        for field in ['email', 'first_name', 'last_name']:
            if field in data:
                setattr(user, field, data[field])
        
        user.save()
        
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined
        })
    
    def put(self, request):
        return self.patch(request)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not request.user.check_password(current_password):
            return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != confirm_password:
            return Response({'error': 'New passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({'error': 'Password must be at least 8 characters long'}, status=status.HTTP_400_BAD_REQUEST)
        
        request.user.set_password(new_password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        
        return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)