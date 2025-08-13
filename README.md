# 🚀 Stock Price Alerting System

A comprehensive Django-based system for monitoring stock prices and sending alerts when specific conditions are met. Built with Django REST Framework and APScheduler for efficient background processing.

## ✨ Features

- **Real-time Stock Monitoring**: Track 10 major stocks with live price updates
- **Smart Alert System**: 
  - Threshold alerts (e.g., "Notify when AAPL > $200")
  - Duration alerts (e.g., "Alert when TSLA stays below $600 for 2 hours")
- **Email Notifications**: Gmail SMTP integration for instant alerts
- **JWT Authentication**: Secure user management and API access
- **Background Processing**: APScheduler for stock updates and alert checking
- **RESTful API**: Complete CRUD operations for alerts and user management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Django App    │    │   APScheduler   │    │   PostgreSQL    │
│                 │    │   (Background   │    │   Database      │
│ - REST API      │◄──►│    Tasks)       │◄──►│                 │
│ - User Auth     │    │ - Stock Updates │    │                 │
│ - Alert Logic   │    │ - Alert Checks  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Email SMTP    │    │  Twelve Data    │
│   Service       │    │     API         │
└─────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Task Scheduling**: APScheduler
- **Stock Data**: Twelve Data API
- **Email**: Gmail SMTP

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL
- Twelve Data API key

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd stockAlerter
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file in `stockAlertSystem/stockAlertSystem/`:

```env
# Django Settings
SECRET_KEY=your_secret_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Settings
DB_NAME=stock_alert_db
DB_USER=stockuser
DB_PASSWORD=stockUser
DB_HOST=localhost
DB_PORT=5432

# Twelve Data API
TWELVE_DATA_API_KEY=your_actual_api_key_here

# Email Settings (Gmail SMTP)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
```

### 3. Database Setup

```bash
# Create PostgreSQL database
createdb stock_alert_db

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

### 4. Initialize Stocks

```bash
# Initialize default stock list
python manage.py init_stocks --fetch-prices
```

### 5. Start Services

```bash
# Start Django server
python manage.py runserver
```

## 📚 API Endpoints

### Authentication
```
POST /api/token/              # Login (get JWT token)
POST /api/token/refresh/      # Refresh JWT token
```

### User Management
```
POST /api/accounts/register/  # User registration
GET  /api/accounts/profile/   # User profile (authenticated)
```

### Alerts
```
GET    /api/alerts/alerts/           # List user alerts
POST   /api/alerts/alerts/           # Create new alert
GET    /api/alerts/alerts/{id}/      # Get specific alert
PUT    /api/alerts/alerts/{id}/      # Update alert
DELETE /api/alerts/alerts/{id}/      # Delete alert
POST   /api/alerts/alerts/{id}/check_condition/  # Check alert condition
POST   /api/alerts/alerts/{id}/toggle_active/    # Toggle alert status
GET    /api/alerts/alerts/active/    # Get active alerts only
GET    /api/alerts/alerts/triggered/ # Get triggered alerts
```

### Stocks
```
GET  /api/stocks/stocks/             # List stocks
POST /api/stocks/update_price/       # Update stock price
```

## 🔧 Management Commands

```bash
# Initialize default stocks
python manage.py init_stocks --fetch-prices

# Update all stock prices
python manage.py update_prices

# Update specific stock price
python manage.py update_prices --symbol AAPL
```

## 📊 Alert Types

### 1. Threshold Alerts
Trigger immediately when a condition is met:
- **Above**: Notify when stock price goes above target
- **Below**: Notify when stock price goes below target  
- **Equals**: Notify when stock price equals target

### 2. Duration Alerts
Trigger after a condition has been met for a specified duration:
- **Example**: Alert when TSLA stays below $600 for 2 hours
- **Use Case**: Avoid false alarms from temporary price movements

## 🔄 Background Tasks

### Scheduled Tasks
- **Stock Price Updates**: Every 5 minutes
- **Alert Checking**: Every minute
- **Alert Reset**: Every hour (resets triggered alerts)

## 🧪 Testing

```bash
# Run tests
python manage.py test

# Test specific app
python manage.py test alerts
python manage.py test stocks
```

## 📈 Performance Optimization

- **Database Indexing**: Stock price queries are indexed for performance
- **Select Related**: API responses use select_related to minimize queries
- **Task Scheduling**: Efficient APScheduler configuration

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **User Isolation**: Users can only access their own alerts
- **Input Validation**: Comprehensive serializer validation
- **SQL Injection Protection**: Django ORM protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section

---
**Happy Stock Monitoring! 📊📈**
