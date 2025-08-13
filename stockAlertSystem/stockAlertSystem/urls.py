from django.contrib import admin
from django.urls import path,include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/accounts/', include('accounts.urls', namespace='accounts')),  
    path('api/stocks/', include('stocks.urls', namespace='stocks')),
    path('api/alerts/', include('alerts.urls', namespace='alerts')),
    path('api/scheduler/', include('scheduler.urls', namespace='scheduler')),
    path('api/notifications/', include('notifications.urls', namespace='notifications')),
]
