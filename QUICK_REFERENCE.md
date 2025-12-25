# Citizen Report API - Quick Reference Card

## 🎯 Base URL

```
http://localhost:8000/api/reports/
```

---

## 📋 Endpoints

### 1. Create Report (Submit Issue)

```http
POST /api/reports/
Content-Type: multipart/form-data
```

**Form Data:**

```
reporter_name: "John Doe"
issue_type: "traffic"     # choices: traffic, waste, energy, other
description: "Issue description"
location: "Location address"
image: [file]            # optional
```

**cURL:**

```bash
curl -X POST http://localhost:8000/api/reports/ \
  -F "reporter_name=John Doe" \
  -F "issue_type=traffic" \
  -F "description=Heavy congestion" \
  -F "location=Main Street" \
  -F "image=@photo.jpg"
```

**JavaScript:**

```javascript
const formData = new FormData();
formData.append('reporter_name', 'John Doe');
formData.append('issue_type', 'traffic');
formData.append('description', 'Heavy congestion');
formData.append('location', 'Main Street');
formData.append('image', fileInput.files[0]);

fetch('http://localhost:8000/api/reports/', {
	method: 'POST',
	body: formData,
});
```

---

### 2. List All Reports

```http
GET /api/reports/
```

**Example:**

```bash
curl http://localhost:8000/api/reports/
```

---

### 3. Filter Reports

#### By Status

```bash
GET /api/reports/?status=pending
```

Status options: `pending`, `in_progress`, `resolved`, `rejected`

#### By Issue Type

```bash
GET /api/reports/?issue_type=traffic
```

Issue types: `traffic`, `waste`, `energy`, `other`

#### Multiple Filters

```bash
GET /api/reports/?status=pending&issue_type=waste
```

#### Custom Ordering

```bash
# Latest first (default)
GET /api/reports/?ordering=-created_at

# Oldest first
GET /api/reports/?ordering=created_at
```

---

### 4. Get Single Report

```http
GET /api/reports/{id}/
```

**Example:**

```bash
curl http://localhost:8000/api/reports/1/
```

---

### 5. Update Report Status (Admin)

```http
PATCH /api/reports/{id}/
Content-Type: application/json
```

**Request:**

```json
{
	"status": "in_progress"
}
```

**cURL:**

```bash
curl -X PATCH http://localhost:8000/api/reports/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "resolved"}'
```

---

## 📊 Response Format

```json
{
	"id": 1,
	"reporter_name": "John Doe",
	"issue_type": "traffic",
	"issue_type_display": "Traffic Issue",
	"description": "Heavy traffic congestion",
	"image": "/media/citizen_reports/2025/12/25/photo.jpg",
	"location": "Main Street",
	"status": "pending",
	"status_display": "Pending Review",
	"created_at": "2025-12-25T10:30:00Z",
	"updated_at": "2025-12-25T10:30:00Z"
}
```

---

## 🔑 Field Reference

| Field           | Type     | Required  | Notes                         |
| --------------- | -------- | --------- | ----------------------------- |
| `reporter_name` | string   | Yes       | Name of person reporting      |
| `issue_type`    | string   | Yes       | traffic/waste/energy/other    |
| `description`   | string   | Yes       | Issue details                 |
| `location`      | string   | Yes       | Location address              |
| `image`         | file     | No        | Image upload (jpg, png, etc.) |
| `status`        | string   | Read-only | Defaults to 'pending'         |
| `created_at`    | datetime | Auto      | Timestamp                     |
| `updated_at`    | datetime | Auto      | Timestamp                     |

---

## 🎨 Issue Types

| Value     | Display            |
| --------- | ------------------ |
| `traffic` | Traffic Issue      |
| `waste`   | Waste Management   |
| `energy`  | Energy/Power Issue |
| `other`   | Other              |

---

## 📌 Status Values

| Value         | Display        |
| ------------- | -------------- |
| `pending`     | Pending Review |
| `in_progress` | In Progress    |
| `resolved`    | Resolved       |
| `rejected`    | Rejected       |

---

## 🧪 Quick Test

### 1. Install & Setup

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### 2. Create Sample Report

```bash
curl -X POST http://localhost:8000/api/reports/ \
  -F "reporter_name=Test User" \
  -F "issue_type=traffic" \
  -F "description=Test issue" \
  -F "location=Test Location"
```

### 3. List Reports

```bash
curl http://localhost:8000/api/reports/
```

### 4. Filter by Status

```bash
curl "http://localhost:8000/api/reports/?status=pending"
```

### 5. Run Full Test Suite

```bash
python test_citizen_reports.py
```

---

## 🚀 Integration Tips

### React Example

```jsx
const submitReport = async (formData) => {
	const response = await fetch('http://localhost:8000/api/reports/', {
		method: 'POST',
		body: formData, // FormData object
	});
	return await response.json();
};
```

### Vue Example

```javascript
async submitReport(formData) {
  const response = await this.$http.post('/api/reports/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  });
  return response.data;
}
```

### Angular Example

```typescript
submitReport(formData: FormData): Observable<any> {
  return this.http.post('http://localhost:8000/api/reports/', formData);
}
```

---

## 📚 Documentation

-   **Full API Docs**: [`CITIZEN_REPORT_API.md`](CITIZEN_REPORT_API.md)
-   **Implementation**: [`CITIZEN_REPORT_IMPLEMENTATION.md`](CITIZEN_REPORT_IMPLEMENTATION.md)
-   **Test Script**: [`test_citizen_reports.py`](test_citizen_reports.py)

---

## 💾 Media Files

Images are saved to: `/media/citizen_reports/YYYY/MM/DD/`

Access via: `http://localhost:8000/media/citizen_reports/2025/12/25/image.jpg`

---

## ⚠️ Common Issues

### CORS Errors

Already configured in `settings.py`:

```python
CORS_ALLOW_ALL_ORIGINS = True  # for development
```

### Media Files Not Found

Check `core/urls.py` has:

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### Import Errors

Install dependencies:

```bash
pip install -r requirements.txt
```

---

**Happy Coding! 🎉**
