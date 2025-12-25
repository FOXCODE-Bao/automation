# Newsletter Subscription Feature - Documentation

## Overview

The Newsletter Subscription feature allows citizens to subscribe to receive future alerts from the Smart City system by providing their email addresses.

---

## Implementation Summary

### ✅ What Was Implemented

#### 1. **Model** (`api/models.py`)

-   Created `Subscriber` model with:
    -   `email` (EmailField, unique, max_length=255)
    -   `created_at` (DateTimeField, auto_now_add=True)
    -   String representation returns the email
    -   Proper indexing for performance
    -   Meta ordering by latest first

#### 2. **Serializer** (`api/serializers.py`)

-   Created `SubscriberSerializer` with:
    -   Email format validation
    -   Automatic lowercase conversion and trimming
    -   Unique constraint handling with clear error messages
    -   Read-only fields for `id` and `created_at`

#### 3. **View** (`api/views.py`)

-   Created `SubscribeView` (CreateAPIView) with:
    -   `POST /api/subscribe/` endpoint
    -   Duplicate email detection
    -   Returns HTTP 400 for already subscribed emails
    -   Returns HTTP 201 for successful subscriptions
    -   Proper logging for monitoring
    -   AllowAny permissions (public endpoint)

#### 4. **URL** (`api/urls.py`)

-   Added `/api/subscribe/` endpoint
-   Configured route to SubscribeView

---

## API Endpoint

### Subscribe to Newsletter

**Endpoint:**

```
POST /api/subscribe/
```

**Content-Type:** `application/json`

**Request Body:**

```json
{
	"email": "user@example.com"
}
```

**Success Response (201 Created):**

```json
{
	"success": true,
	"message": "Successfully subscribed to newsletter!",
	"data": {
		"id": 1,
		"email": "user@example.com",
		"created_at": "2025-12-25T10:30:00Z"
	}
}
```

**Error Response - Already Subscribed (400 Bad Request):**

```json
{
	"error": "Already subscribed",
	"message": "This email is already subscribed to our newsletter."
}
```

**Error Response - Invalid Email (400 Bad Request):**

```json
{
	"email": ["Enter a valid email address."]
}
```

**Error Response - Missing Email (400 Bad Request):**

```json
{
	"email": ["This field is required."]
}
```

---

## Testing

### Using cURL

#### Successful Subscription

```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com"}'
```

**Expected Output:**

```json
{
	"success": true,
	"message": "Successfully subscribed to newsletter!",
	"data": {
		"id": 1,
		"email": "john@example.com",
		"created_at": "2025-12-25T10:30:00Z"
	}
}
```

#### Duplicate Subscription Attempt

```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "john@example.com"}'
```

**Expected Output:**

```json
{
	"error": "Already subscribed",
	"message": "This email is already subscribed to our newsletter."
}
```

#### Invalid Email Format

```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "invalid-email"}'
```

**Expected Output:**

```json
{
	"email": ["Enter a valid email address."]
}
```

---

### Using Python requests

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"

def subscribe_to_newsletter(email):
    """Subscribe to newsletter."""
    url = f"{BASE_URL}/subscribe/"
    data = {"email": email}

    response = requests.post(url, json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response

# Test cases
print("=== Test 1: Valid subscription ===")
subscribe_to_newsletter("user1@example.com")

print("\n=== Test 2: Duplicate subscription ===")
subscribe_to_newsletter("user1@example.com")

print("\n=== Test 3: Invalid email ===")
subscribe_to_newsletter("not-an-email")

print("\n=== Test 4: Different valid email ===")
subscribe_to_newsletter("user2@example.com")
```

---

### Using JavaScript (Fetch API)

```javascript
async function subscribeToNewsletter(email) {
	try {
		const response = await fetch('http://localhost:8000/api/subscribe/', {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
			},
			body: JSON.stringify({ email }),
		});

		const data = await response.json();

		if (response.ok) {
			console.log('Success:', data.message);
			return { success: true, data };
		} else {
			console.error('Error:', data.message || data.email);
			return { success: false, error: data };
		}
	} catch (error) {
		console.error('Network error:', error);
		return { success: false, error: error.message };
	}
}

// Usage
subscribeToNewsletter('user@example.com');
```

---

### React Example

```jsx
import React, { useState } from 'react';

function NewsletterSubscription() {
	const [email, setEmail] = useState('');
	const [message, setMessage] = useState('');
	const [isError, setIsError] = useState(false);
	const [loading, setLoading] = useState(false);

	const handleSubmit = async (e) => {
		e.preventDefault();
		setLoading(true);
		setMessage('');

		try {
			const response = await fetch(
				'http://localhost:8000/api/subscribe/',
				{
					method: 'POST',
					headers: {
						'Content-Type': 'application/json',
					},
					body: JSON.stringify({ email }),
				}
			);

			const data = await response.json();

			if (response.ok) {
				setMessage(data.message);
				setIsError(false);
				setEmail(''); // Clear input
			} else {
				setMessage(
					data.message || data.email?.[0] || 'Subscription failed'
				);
				setIsError(true);
			}
		} catch (error) {
			setMessage('Network error. Please try again.');
			setIsError(true);
		} finally {
			setLoading(false);
		}
	};

	return (
		<div className="newsletter-subscription">
			<h3>Subscribe to Alerts</h3>
			<form onSubmit={handleSubmit}>
				<input
					type="email"
					placeholder="Enter your email"
					value={email}
					onChange={(e) => setEmail(e.target.value)}
					required
					disabled={loading}
				/>
				<button type="submit" disabled={loading}>
					{loading ? 'Subscribing...' : 'Subscribe'}
				</button>
			</form>
			{message && (
				<p className={isError ? 'error' : 'success'}>{message}</p>
			)}
		</div>
	);
}

export default NewsletterSubscription;
```

---

## Database Setup

### Run Migrations

After implementing the feature, run:

```bash
# Create migration file
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

**Expected Output:**

```
Migrations for 'api':
  api/migrations/0002_subscriber.py
    - Create model Subscriber
Running migrations:
  Applying api.0002_subscriber... OK
```

---

## Model Details

### Subscriber Model

```python
class Subscriber(models.Model):
    """
    Model for newsletter subscribers.
    Citizens can subscribe to receive future alerts from the system.
    """

    email = models.EmailField(
        unique=True,
        max_length=255,
        help_text="Email address for newsletter subscription",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Subscriber"
        verbose_name_plural = "Subscribers"
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return self.email
```

**Key Features:**

-   ✅ Unique email constraint (prevents duplicates at DB level)
-   ✅ Indexed for query performance
-   ✅ Automatic timestamp tracking
-   ✅ Ordered by newest first

---

## Admin Integration (Optional)

To manage subscribers in Django Admin, add to `api/admin.py`:

```python
from django.contrib import admin
from .models import Subscriber

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'created_at']
    search_fields = ['email']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
```

---

## Security Considerations

### ✅ Implemented

-   Email format validation
-   Unique constraint (prevents duplicate subscriptions)
-   Lowercase normalization (case-insensitive emails)
-   Whitespace trimming
-   Public endpoint (AllowAny) - appropriate for newsletter signup

### 🔒 Production Recommendations

1. **Rate Limiting**: Add rate limiting to prevent spam

    ```python
    # In settings.py
    REST_FRAMEWORK = {
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '10/hour',  # 10 subscriptions per hour per IP
        }
    }
    ```

2. **Email Verification**: Add email confirmation process

    - Send verification email with token
    - Activate subscription only after verification

3. **GDPR Compliance**: Add unsubscribe functionality

    - Store consent timestamp
    - Provide unsubscribe endpoint
    - Handle data deletion requests

4. **CAPTCHA**: Add reCAPTCHA to prevent bot subscriptions

5. **Logging**: Monitor for suspicious patterns
    - Already implemented basic logging

---

## Future Enhancements

### 1. Unsubscribe Endpoint

```python
# DELETE /api/unsubscribe/{email}/
class UnsubscribeView(generics.DestroyAPIView):
    queryset = Subscriber.objects.all()
    lookup_field = 'email'
```

### 2. Email Verification

```python
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### 3. List Subscribers (Admin Only)

```python
# GET /api/subscribers/
class SubscriberListView(generics.ListAPIView):
    queryset = Subscriber.objects.all()
    serializer_class = SubscriberSerializer
    permission_classes = [IsAdminUser]
```

### 4. Subscriber Preferences

```python
class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    receive_traffic_alerts = models.BooleanField(default=True)
    receive_energy_alerts = models.BooleanField(default=True)
    receive_waste_alerts = models.BooleanField(default=True)
```

---

## Error Handling

The implementation handles various error cases:

| Scenario                | HTTP Status               | Response                     |
| ----------------------- | ------------------------- | ---------------------------- |
| Successful subscription | 201 Created               | Success message with data    |
| Duplicate email         | 400 Bad Request           | "Already subscribed" message |
| Invalid email format    | 400 Bad Request           | Validation error             |
| Missing email field     | 400 Bad Request           | "This field is required"     |
| Server error            | 500 Internal Server Error | Error details                |

---

## Quick Start

### 1. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Start Server

```bash
python manage.py runserver
```

### 3. Test Subscription

```bash
curl -X POST http://localhost:8000/api/subscribe/ \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}'
```

### 4. Check Django Admin

```bash
# Create superuser if needed
python manage.py createsuperuser

# Access admin panel
http://localhost:8000/admin/
```

---

## Integration with Frontend

The subscription feature is ready for frontend integration:

**Endpoint:** `POST /api/subscribe/`  
**Input:** `{ "email": "user@example.com" }`  
**Output:** Success/error message with data

---

## Summary

✅ **Model**: Subscriber with unique email and timestamp  
✅ **Serializer**: Validation and error handling  
✅ **View**: CreateAPIView with duplicate detection  
✅ **URL**: `/api/subscribe/` endpoint  
✅ **Security**: Email validation and normalization  
✅ **Testing**: Ready for cURL, Python, and JavaScript testing

**Status:** ✅ **Implementation Complete**

The Newsletter Subscription feature is fully implemented and ready for use! 🎉
