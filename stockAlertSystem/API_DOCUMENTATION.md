# 📚 Stock Price Alerting System API Documentation

This document provides comprehensive documentation for all API endpoints in the Stock Price Alerting System.

## 🔐 Authentication

The API uses JWT (JSON Web Token) authentication. All protected endpoints require a valid JWT token in the Authorization header.

### Getting Started

1. **Register a new user** (POST `/api/accounts/register/`)
2. **Login** (POST `/api/accounts/login/`) to get JWT tokens
3. **Include token** in subsequent requests: `Authorization: Bearer <access_token>`

### Token Types

- **Access Token**: Short-lived (15 minutes), used for API requests
- **Refresh Token**: Long-lived (7 days), used to get new access tokens

## 📊 API Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/accounts/register/` | User registration | No |
| POST | `/api/accounts/login/` | User login | No |
| POST | `/api/accounts/token/refresh/` | Refresh access token | No |
| GET | `/api/accounts/profile/` | Get user profile | Yes |
| PATCH | `/api/accounts/profile/` | Update user profile | Yes |
| POST | `/api/accounts/change-password/` | Change password | Yes |
| GET | `/api/stocks/` | List all stocks | Yes |
| GET | `/api/stocks/{id}/` | Get stock details | Yes |
| POST | `/api/stocks/update-price/` | Update stock price | Yes |
| GET | `/api/alerts/` | List user alerts | Yes |
| POST | `/api/alerts/` | Create new alert | Yes |
| GET | `/api/alerts/{id}/` | Get alert details | Yes |
| PATCH | `/api/alerts/{id}/` | Update alert | Yes |
| DELETE | `/api/alerts/{id}/` | Delete alert | Yes |
| POST | `/api/alerts/{id}/toggle-active/` | Toggle alert status | Yes |
| GET | `/api/alerts/history/` | Get alert history | Yes |

## 👤 Accounts API

### User Registration

**Endpoint:** `POST /api/accounts/register/`

**Description:** Register a new user account

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```

**Response (201 Created):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "date_joined": "2024-01-15T10:30:00Z"
    }
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Username already exists"
}
```

### User Login

**Endpoint:** `POST /api/accounts/login/`

**Description:** Authenticate user and get JWT tokens

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "date_joined": "2024-01-15T10:30:00Z"
    }
}
```

**Error Response (401 Unauthorized):**
```json
{
    "error": "Invalid credentials"
}
```

### Token Refresh

**Endpoint:** `POST /api/accounts/token/refresh/`

**Description:** Get new access token using refresh token

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Get User Profile

**Endpoint:** `GET /api/accounts/profile/`

**Description:** Get current user's profile information

**Headers:** `Authorization: Bearer <access_token>`

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T15:45:00Z"
}
```

### Update User Profile

**Endpoint:** `PATCH /api/accounts/profile/`

**Description:** Update current user's profile information

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "first_name": "Johnny",
    "last_name": "Smith",
    "email": "johnny@example.com"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "johnny@example.com",
    "first_name": "Johnny",
    "last_name": "Smith",
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T15:45:00Z"
}
```

### Change Password

**Endpoint:** `POST /api/accounts/change-password/`

**Description:** Change current user's password

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "current_password": "securepassword123",
    "new_password": "newsecurepassword456",
    "new_password_confirm": "newsecurepassword456"
}
```

**Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

## 📈 Stocks API

### List All Stocks

**Endpoint:** `GET /api/stocks/`

**Description:** Get list of all available stocks

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `search`: Search by symbol or name
- `exchange`: Filter by exchange
- `is_active`: Filter by active status

**Response (200 OK):**
```json
{
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "price": "150.25",
            "last_updated": "2024-01-15T15:30:00Z",
            "is_active": true
        },
        {
            "id": 2,
            "symbol": "GOOGL",
            "name": "Alphabet Inc.",
            "exchange": "NASDAQ",
            "currency": "USD",
            "price": "2750.50",
            "last_updated": "2024-01-15T15:30:00Z",
            "is_active": true
        }
    ]
}
```

### Get Stock Details

**Endpoint:** `GET /api/stocks/{id}/`

**Description:** Get detailed information about a specific stock

**Headers:** `Authorization: Bearer <access_token>`

**Response (200 OK):**
```json
{
    "id": 1,
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "exchange": "NASDAQ",
    "currency": "USD",
    "price": "150.25",
    "last_updated": "2024-01-15T15:30:00Z",
    "is_active": true,
    "price_history": [
        {
            "id": 1,
            "price": "150.25",
            "timestamp": "2024-01-15T15:30:00Z"
        },
        {
            "id": 2,
            "price": "149.80",
            "timestamp": "2024-01-15T15:25:00Z"
        }
    ]
}
```

### Update Stock Price

**Endpoint:** `POST /api/stocks/update-price/`

**Description:** Manually trigger stock price update

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "symbol": "AAPL"
}
```

**Response (200 OK):**
```json
{
    "message": "Stock price update initiated",
    "task_id": "task-uuid-here",
    "symbol": "AAPL"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Invalid stock symbol"
}
```

## 🚨 Alerts API

### List User Alerts

**Endpoint:** `GET /api/alerts/`

**Description:** Get list of current user's alerts

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `alert_type`: Filter by alert type (`threshold` or `duration`)
- `status`: Filter by status (`active`, `triggered`, `inactive`)
- `stock`: Filter by stock symbol
- `is_active`: Filter by active status

**Response (200 OK):**
```json
{
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "stock": {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc."
            },
            "alert_type": "threshold",
            "condition": "above",
            "target_price": "200.00",
            "duration_minutes": null,
            "status": "active",
            "is_active": true,
            "created_at": "2024-01-15T10:00:00Z",
            "description": "Alert when AAPL goes above $200.00"
        },
        {
            "id": 2,
            "stock": {
                "id": 2,
                "symbol": "GOOGL",
                "name": "Alphabet Inc."
            },
            "alert_type": "duration",
            "condition": "below",
            "target_price": "2700.00",
            "duration_minutes": 120,
            "status": "active",
            "is_active": true,
            "created_at": "2024-01-15T11:00:00Z",
            "description": "Alert when GOOGL stays below $2700.00 for 120 minutes"
        }
    ]
}
```

### Create New Alert

**Endpoint:** `POST /api/alerts/`

**Description:** Create a new stock price alert

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "stock": 1,
    "alert_type": "threshold",
    "condition": "above",
    "target_price": "200.00"
}
```

**For Duration Alert:**
```json
{
    "stock": 2,
    "alert_type": "duration",
    "condition": "below",
    "target_price": "2700.00",
    "duration_minutes": 120
}
```

**Response (201 Created):**
```json
{
    "id": 3,
    "stock": {
        "id": 1,
        "symbol": "AAPL",
        "name": "Apple Inc."
    },
    "alert_type": "threshold",
    "condition": "above",
    "target_price": "200.00",
    "duration_minutes": null,
    "status": "active",
    "is_active": true,
    "created_at": "2024-01-15T12:00:00Z",
    "description": "Alert when AAPL goes above $200.00"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Invalid alert configuration",
    "details": {
        "target_price": ["This field is required."],
        "stock": ["This field is required."]
    }
}
```

### Get Alert Details

**Endpoint:** `GET /api/alerts/{id}/`

**Description:** Get detailed information about a specific alert

**Headers:** `Authorization: Bearer <access_token>`

**Response (200 OK):**
```json
{
    "id": 1,
    "stock": {
        "id": 1,
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "current_price": "150.25"
    },
    "alert_type": "threshold",
    "condition": "above",
    "target_price": "200.00",
    "duration_minutes": null,
    "status": "active",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z",
    "last_checked": "2024-01-15T15:30:00Z",
    "description": "Alert when AAPL goes above $200.00"
}
```

### Update Alert

**Endpoint:** `PATCH /api/alerts/{id}/`

**Description:** Update an existing alert

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
    "target_price": "250.00",
    "condition": "above"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "stock": {
        "id": 1,
        "symbol": "AAPL",
        "name": "Apple Inc."
    },
    "alert_type": "threshold",
    "condition": "above",
    "target_price": "250.00",
    "duration_minutes": null,
    "status": "active",
    "is_active": true,
    "created_at": "2024-01-15T10:00:00Z",
    "description": "Alert when AAPL goes above $250.00"
}
```

### Delete Alert

**Endpoint:** `DELETE /api/alerts/{id}/`

**Description:** Delete an alert

**Headers:** `Authorization: Bearer <access_token>`

**Response (204 No Content):** No response body

### Toggle Alert Active Status

**Endpoint:** `POST /api/alerts/{id}/toggle-active/`

**Description:** Toggle alert active/inactive status

**Headers:** `Authorization: Bearer <access_token>`

**Response (200 OK):**
```json
{
    "id": 1,
    "is_active": false,
    "message": "Alert deactivated successfully"
}
```

### Get Alert History

**Endpoint:** `GET /api/alerts/history/`

**Description:** Get history of triggered alerts

**Headers:** `Authorization: Bearer <access_token>`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20)
- `alert`: Filter by alert ID
- `stock`: Filter by stock symbol
- `date_from`: Filter from date (YYYY-MM-DD)
- `date_to`: Filter to date (YYYY-MM-DD)

**Response (200 OK):**
```json
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "alert": {
                "id": 1,
                "description": "Alert when AAPL goes above $200.00"
            },
            "stock": {
                "id": 1,
                "symbol": "AAPL",
                "name": "Apple Inc."
            },
            "stock_price": "210.50",
            "message": "AAPL price ($210.50) exceeded threshold ($200.00)",
            "triggered_at": "2024-01-15T14:30:00Z",
            "notification_sent": true
        },
        {
            "id": 2,
            "alert": {
                "id": 2,
                "description": "Alert when GOOGL stays below $2700.00 for 120 minutes"
            },
            "stock": {
                "id": 2,
                "symbol": "GOOGL",
                "name": "Alphabet Inc."
            },
            "stock_price": "2650.00",
            "message": "GOOGL price ($2650.00) stayed below threshold ($2700.00) for 120 minutes",
            "triggered_at": "2024-01-15T13:45:00Z",
            "notification_sent": true
        }
    ]
}
```

## 🔧 Error Handling

### Standard Error Response Format

```json
{
    "error": "Error message description",
    "details": {
        "field_name": ["Specific field error message"]
    },
    "code": "ERROR_CODE"
}
```

### HTTP Status Codes

| Status Code | Description |
|-------------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 204 | No Content - Request successful, no response body |
| 400 | Bad Request - Invalid request data |
| 401 | Unauthorized - Authentication required |
| 403 | Forbidden - Access denied |
| 404 | Not Found - Resource not found |
| 429 | Too Many Requests - Rate limit exceeded |
| 500 | Internal Server Error - Server error |

### Common Error Codes

| Error Code | Description |
|------------|-------------|
| `INVALID_CREDENTIALS` | Username/password incorrect |
| `TOKEN_EXPIRED` | JWT token has expired |
| `INVALID_TOKEN` | JWT token is invalid |
| `PERMISSION_DENIED` | User lacks permission for action |
| `RESOURCE_NOT_FOUND` | Requested resource doesn't exist |
| `VALIDATION_ERROR` | Request data validation failed |
| `RATE_LIMIT_EXCEEDED` | API rate limit exceeded |

## 📝 Request/Response Examples

### Complete Alert Creation Flow

1. **Login to get token:**
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "johndoe", "password": "password123"}'
```

2. **Create alert using token:**
```bash
curl -X POST http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "stock": 1,
    "alert_type": "threshold",
    "condition": "above",
    "target_price": "200.00"
  }'
```

3. **List user alerts:**
```bash
curl -X GET http://localhost:8000/api/alerts/ \
  -H "Authorization: Bearer <access_token>"
```

### Python Examples

```python
import requests

# Base URL
BASE_URL = "http://localhost:8000/api"

# Login
login_data = {
    "username": "johndoe",
    "password": "password123"
}
response = requests.post(f"{BASE_URL}/accounts/login/", json=login_data)
tokens = response.json()
access_token = tokens["access"]

# Headers for authenticated requests
headers = {
    "Authorization": f"Bearer {access_token}",
    "Content-Type": "application/json"
}

# Create alert
alert_data = {
    "stock": 1,
    "alert_type": "threshold",
    "condition": "above",
    "target_price": "200.00"
}
response = requests.post(f"{BASE_URL}/alerts/", json=alert_data, headers=headers)
print(response.json())

# List alerts
response = requests.get(f"{BASE_URL}/alerts/", headers=headers)
alerts = response.json()
for alert in alerts["results"]:
    print(f"{alert['stock']['symbol']}: {alert['description']}")
```

### JavaScript Examples

```javascript
const BASE_URL = "http://localhost:8000/api";

// Login function
async function login(username, password) {
    const response = await fetch(`${BASE_URL}/accounts/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    });
    
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data;
}

// Create alert function
async function createAlert(alertData) {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${BASE_URL}/alerts/`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(alertData)
    });
    
    return response.json();
}

// Usage
login('johndoe', 'password123').then(() => {
    createAlert({
        stock: 1,
        alert_type: 'threshold',
        condition: 'above',
        target_price: '200.00'
    }).then(alert => {
        console.log('Alert created:', alert);
    });
});
```

## 📊 Rate Limiting

- **Authentication endpoints**: 100 requests per hour
- **API endpoints**: 1000 requests per hour per user
- **Stock price updates**: 10 requests per minute per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642248000
```

## 🔒 Security Considerations

1. **HTTPS Required**: All production endpoints must use HTTPS
2. **Token Expiration**: Access tokens expire after 15 minutes
3. **Input Validation**: All input is validated and sanitized
4. **SQL Injection Protection**: Uses Django ORM with parameterized queries
5. **XSS Protection**: Output is properly escaped
6. **CSRF Protection**: Enabled for all state-changing operations

## 📚 Additional Resources

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [JWT Authentication Guide](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Stock Market Data APIs](https://twelvedata.com/docs)

## 🆘 Support

For API support and questions:
1. Check the error messages and status codes
2. Verify your authentication token is valid
3. Ensure request data matches the expected format
4. Check rate limiting headers
5. Review the Django logs for detailed error information
