# Citizen Report API Documentation

## Overview

The Citizen Report feature allows citizens to submit issues related to city services and provides an API for administrators to view reports on a statistics dashboard.

**Important:** This feature is **standalone** and does **NOT** interact with n8n. It only saves data to the database.

---

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This includes `django-filter` for filtering support.

### 2. Add to INSTALLED_APPS

In `core/settings.py`, ensure these apps are included (already configured):

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'corsheaders',
    'django_filters',  # Add this line if not present
    'api',
]
```

### 3. Media Configuration (Already Configured)

In `core/settings.py`:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

In `core/urls.py` (for development):

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## API Endpoints

The CitizenReportViewSet provides the following endpoints:

| Method | Endpoint             | Description                     |
| ------ | -------------------- | ------------------------------- |
| GET    | `/api/reports/`      | List all reports with filtering |
| POST   | `/api/reports/`      | Create a new report             |
| GET    | `/api/reports/{id}/` | Retrieve a specific report      |
| PUT    | `/api/reports/{id}/` | Update a report (full)          |
| PATCH  | `/api/reports/{id}/` | Update a report (partial)       |
| DELETE | `/api/reports/{id}/` | Delete a report                 |

---

## 1. Create Report (POST)

### Endpoint

```
POST /api/reports/
```

### Content-Type

-   `multipart/form-data` (for image uploads)
-   `application/json` (for JSON data without images)

### Request Body (Form-data)

```
reporter_name: "John Doe"
issue_type: "traffic"
description: "Heavy traffic congestion on Main Street"
location: "Main Street, Downtown"
image: [file upload] (optional)
```

### Request Example (cURL with image)

```bash
curl -X POST http://localhost:8000/api/reports/ \
  -F "reporter_name=John Doe" \
  -F "issue_type=traffic" \
  -F "description=Heavy traffic congestion" \
  -F "location=Main Street" \
  -F "image=@/path/to/image.jpg"
```

### Request Example (JavaScript with image)

```javascript
const formData = new FormData();
formData.append('reporter_name', 'John Doe');
formData.append('issue_type', 'traffic');
formData.append('description', 'Heavy traffic congestion');
formData.append('location', 'Main Street');
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8000/api/reports/', {
	method: 'POST',
	body: formData,
})
	.then((response) => response.json())
	.then((data) => console.log(data));
```

### Response (201 Created)

```json
{
	"id": 1,
	"reporter_name": "John Doe",
	"issue_type": "traffic",
	"issue_type_display": "Traffic Issue",
	"description": "Heavy traffic congestion",
	"image": "/media/citizen_reports/2025/12/25/image.jpg",
	"location": "Main Street",
	"status": "pending",
	"status_display": "Pending Review",
	"created_at": "2025-12-25T10:30:00Z",
	"updated_at": "2025-12-25T10:30:00Z"
}
```

### Issue Type Choices

-   `traffic` - Traffic Issue
-   `waste` - Waste Management
-   `energy` - Energy/Power Issue
-   `other` - Other

### Status (Read-only, defaults to "pending")

-   `pending` - Pending Review
-   `in_progress` - In Progress
-   `resolved` - Resolved
-   `rejected` - Rejected

---

## 2. List Reports (GET)

### Endpoint

```
GET /api/reports/
```

### Query Parameters

#### Filtering

-   `status` - Filter by status (e.g., `?status=pending`)
-   `issue_type` - Filter by issue type (e.g., `?issue_type=traffic`)

#### Ordering

-   `ordering` - Order by field (e.g., `?ordering=-created_at` for latest first)
    -   Available fields: `created_at`, `updated_at`
    -   Use `-` prefix for descending order

### Request Examples

```bash
# Get all reports
GET /api/reports/

# Filter by status
GET /api/reports/?status=pending

# Filter by issue type
GET /api/reports/?issue_type=traffic

# Multiple filters
GET /api/reports/?status=pending&issue_type=waste

# Order by oldest first
GET /api/reports/?ordering=created_at
```

### Response (200 OK)

```json
[
	{
		"id": 2,
		"reporter_name": "Jane Smith",
		"issue_type": "waste",
		"issue_type_display": "Waste Management",
		"description": "Overflowing bin at Park Avenue",
		"image": "/media/citizen_reports/2025/12/25/bin.jpg",
		"location": "Park Avenue",
		"status": "pending",
		"status_display": "Pending Review",
		"created_at": "2025-12-25T11:00:00Z",
		"updated_at": "2025-12-25T11:00:00Z"
	},
	{
		"id": 1,
		"reporter_name": "John Doe",
		"issue_type": "traffic",
		"issue_type_display": "Traffic Issue",
		"description": "Heavy traffic congestion",
		"image": "/media/citizen_reports/2025/12/25/traffic.jpg",
		"location": "Main Street",
		"status": "pending",
		"status_display": "Pending Review",
		"created_at": "2025-12-25T10:30:00Z",
		"updated_at": "2025-12-25T10:30:00Z"
	}
]
```

---

## 3. Retrieve Single Report (GET)

### Endpoint

```
GET /api/reports/{id}/
```

### Response (200 OK)

```json
{
	"id": 1,
	"reporter_name": "John Doe",
	"issue_type": "traffic",
	"issue_type_display": "Traffic Issue",
	"description": "Heavy traffic congestion",
	"image": "/media/citizen_reports/2025/12/25/traffic.jpg",
	"location": "Main Street",
	"status": "pending",
	"status_display": "Pending Review",
	"created_at": "2025-12-25T10:30:00Z",
	"updated_at": "2025-12-25T10:30:00Z"
}
```

---

## 4. Update Report (PATCH/PUT)

### Endpoint

```
PATCH /api/reports/{id}/
PUT /api/reports/{id}/
```

### Note

-   **Admin Use Only** - In production, add proper permission classes
-   Status can be updated to track progress (pending → in_progress → resolved/rejected)

### Request Body (JSON)

```json
{
	"status": "in_progress"
}
```

### Response (200 OK)

```json
{
	"id": 1,
	"reporter_name": "John Doe",
	"issue_type": "traffic",
	"issue_type_display": "Traffic Issue",
	"description": "Heavy traffic congestion",
	"image": "/media/citizen_reports/2025/12/25/traffic.jpg",
	"location": "Main Street",
	"status": "in_progress",
	"status_display": "In Progress",
	"created_at": "2025-12-25T10:30:00Z",
	"updated_at": "2025-12-25T12:00:00Z"
}
```

---

## 5. Delete Report (DELETE)

### Endpoint

```
DELETE /api/reports/{id}/
```

### Response (204 No Content)

No content returned on successful deletion.

---

## Testing the API

### Using Python requests

```python
import requests

# Create a report
data = {
    'reporter_name': 'Test User',
    'issue_type': 'traffic',
    'description': 'Test issue',
    'location': 'Test Location'
}
response = requests.post('http://localhost:8000/api/reports/', data=data)
print(response.json())

# List all reports
response = requests.get('http://localhost:8000/api/reports/')
print(response.json())

# Filter by status
response = requests.get('http://localhost:8000/api/reports/?status=pending')
print(response.json())
```

### Using cURL

```bash
# Create report
curl -X POST http://localhost:8000/api/reports/ \
  -F "reporter_name=Test User" \
  -F "issue_type=traffic" \
  -F "description=Test issue" \
  -F "location=Test Location"

# List all reports
curl http://localhost:8000/api/reports/

# Filter by status
curl http://localhost:8000/api/reports/?status=pending

# Update status
curl -X PATCH http://localhost:8000/api/reports/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

---

## Integration with Dashboard

The dashboard endpoint already includes citizen report statistics:

```
GET /api/dashboard/
```

Returns:

```json
{
  "traffic": { ... },
  "energy": { ... },
  "waste": { ... },
  "reports": {
    "pending_count": 5,
    "total_count": 20,
    "recent": [ /* 5 most recent reports */ ]
  }
}
```

---

## Production Considerations

1. **Authentication & Permissions**

    - Update `permission_classes` to restrict who can update/delete reports
    - Example: `permission_classes = [IsAuthenticatedOrReadOnly]`

2. **File Upload Security**

    - Validate file types and sizes
    - Consider using cloud storage (AWS S3, etc.) for production

3. **Rate Limiting**

    - Implement rate limiting to prevent spam

4. **Image Optimization**

    - Add image compression/resizing before saving

5. **Notifications** (Optional)
    - Add email/SMS notifications for new reports
    - Could integrate with n8n for notifications (separate from saving)

---

## Error Handling

### 400 Bad Request

```json
{
	"reporter_name": ["This field is required."],
	"issue_type": ["Invalid choice."]
}
```

### 404 Not Found

```json
{
	"detail": "Not found."
}
```

### 500 Internal Server Error

```json
{
	"error": "Internal server error",
	"details": "Error message"
}
```
