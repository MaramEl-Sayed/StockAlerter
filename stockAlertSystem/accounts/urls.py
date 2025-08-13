from django.urls import path
from .views import RegisterView, protected_view, UserProfileView, ChangePasswordView, CustomLoginView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('protected/', protected_view, name='protected'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
