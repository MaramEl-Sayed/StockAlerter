# 🧪 Stock Price Alerting System - Complete Testing Guide

## ✅ Quick Testing Instructions

### **Step 1: Local Development Setup**

```bash
# 1. Start services
cd stockAlertSystem
python manage.py runserver

# 2. In another terminal, start scheduler
python manage.py shell
>>> from scheduler.services import start_scheduler
>>> start_scheduler()
>>> exit()
```

### **Step 2: Create Test Environment**

```bash
# Create test user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
>>> exit()
```

### **Step 3: Test Alert Creation**

```bash
# Create test alert
python manage.py shell
>>> from alerts.services import create_alert
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='testuser2')
>>> from stocks.models import Stock
>>> stock = Stock.objects.get(symbol='AAPL')
>>> alert = create_alert(user, 'AAPL', 'threshold', 'above', 200.00)
>>> print(alert)
```

### **Step 4: Test Email Notifications**

```bash
# Test email notification
python manage.py shell
>>> from notifications.services import send_email_notification
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='testuser')
>>> send_email_notification(user.id, "Test Alert", "This is a test alert", None)
```

## 🧪 **Complete Testing Workflow**

### **1. API Testing**

```bash
# 1. Register user
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password_confirm":"testpass123"}'

# 2. Login
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# 3. Create alert
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"stock":1,"alert_type":"threshold","condition":"above","target_price":"200.00"}'
```

### **2. Email Testing**

```bash
# Test email notification
python manage.py shell
>>> from notifications.services import send_email_notification
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='testuser')
>>> send_email_notification(user.id, "Test Alert", "This is a test alert", None)
```

### **3. Manual Testing Commands**

```bash
# Test alert checking
python manage.py shell
>>> from alerts.services import check_all_alerts
>>> result = check_all_alerts()
>>> print(result)
```

## 🎯 **Testing Scenarios**

### **1. Threshold Alert Test**
```bash
# Create threshold alert
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"stock":1,"alert_type":"threshold","condition":"above","target_price":"200.00"}'
```

### **2. Duration Alert Test**
```bash
# Create duration alert
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer <your-token>" \
  -H "Content-Type: application/json" \
  -d '{"stock":1,"alert_type":"duration","condition":"below","target_price":"150.00","duration_minutes":120}'
```

## 🧪 **Testing Checklist**

### **1. Environment Setup**
```bash
# 1. Start services
python manage.py runserver

# 2. Start scheduler
python manage.py shell
>>> from scheduler.services import start_scheduler
>>> start_scheduler()
>>> exit()
```

### **2. Test Email Configuration**
```bash
# Test email settings
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test Subject', 'Test message', 'your-email@gmail.com', ['recipient@example.com'])
```

### **3. Test Alert Creation**
```bash
# Create test alert
python manage.py shell
>>> from alerts.services import create_alert
>>> from django.contrib.auth.models import User
>>> from stocks.models import Stock
>>> user = User.objects.get(username='testuser')
>>> stock = Stock.objects.get(symbol='AAPL')
>>> alert = create_alert(user, 'AAPL', 'threshold', 'above', 200.00)
>>> print(alert)
```

### **4. Test Alert Checking**
```bash
# Check alerts
python manage.py shell
>>> from alerts.services import check_all_alerts
>>> result = check_all_alerts()
>>> print(result)
```

## 📊 **Testing Results Verification**

### **1. Check Email Logs**
```bash
# Check email logs
sudo tail -f /var/log/mail.log
```

### **2. Check Alert History**
```bash
# Check alert history
python manage.py shell
>>> from alerts.models import AlertHistory
>>> history = AlertHistory.objects.filter(alert__user__username='testuser')
>>> for h in history:
>>>     print(f"{h.alert.stock.symbol} - {h.triggered_at} - {h.message}")
```

## 🎯 **Quick Start for Testing

### **1. Local Development**
```bash
# 1. Start services
python manage.py runserver

# 2. Create test user
python manage.py shell
>>> from django.contrib.auth.models import User
>>> user = User.objects.create_user('testuser', 'test@example.com', 'testpass123')
>>> exit()

# 3. Create test alert
python manage.py shell
>>> from alerts.services import create_alert
>>> from django.contrib.auth.models import User
>>> from stocks.models import Stock
>>> user = User.objects.get(username='testuser')
>>> stock = Stock.objects.get(symbol='AAPL')
>>> alert = create_alert(user, 'AAPL', 'threshold', 'above', 200.00)
>>> print(alert)
```

### **2. Test Email Notification**
```bash
# Test email notification
python manage.py shell
>>> from notifications.services import send_email_notification
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='testuser')
>>> send_email_notification(user.id, "Test Alert", "This is a test alert", None)
```

## ✅ **Testing Results**

The system is **fully functional** and ready for testing. All components are in place for:
- ✅ **User registration and login**
- ✅ **Alert creation and management**
- ✅ **Email notifications**
- ✅ **Real-time alert checking**
- ✅ **Complete REST API endpoints**


