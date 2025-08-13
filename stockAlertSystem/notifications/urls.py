from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, EmailTemplateViewSet, NotificationHistoryViewSet

app_name = 'notifications'

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'email-templates', EmailTemplateViewSet, basename='email-template')
router.register(r'history', NotificationHistoryViewSet, basename='notification-history')

urlpatterns = [
    path('', include(router.urls)),
    path('send-test/', NotificationViewSet.as_view({'post': 'send_test_notification'}), name='send-test-notification'),
    path('stats/', NotificationViewSet.as_view({'get': 'notification_stats'}), name='notification-stats'),
]
