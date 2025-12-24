# Smart City API Examples

## Overview

This document provides example requests and responses for the Smart City Dashboard API endpoints.

## Base URL

```
http://localhost:8000/api/
```

---

## 1. n8n Webhook Receiver Endpoint

### Endpoint

```
POST /api/webhook/save-stats/
```

### Purpose

Receives scheduled statistics from n8n workflow and saves to database using atomic transactions.

### Request Example

**cURL:**

```bash
curl -X POST http://localhost:8000/api/webhook/save-stats/ \
  -H "Content-Type: application/json" \
  -d '{
    "energyOptimizationData": {
      "summary": {
        "total_consumption": 150.5,
        "anomalies": true,
        "average_power": 450.2
      },
      "statistics": {
        "voltage": {
          "min": 210,
          "max": 230,
          "average": 220
        }
      }
    },
    "wasteTrackingData": {
      "avgFill": 75.5,
      "criticalCount": 3,
      "warningCount": 5,
      "warningLocations": ["Point A", "Point B"]
    }
  }'
```

**Python (requests):**

```python
import requests

url = "http://localhost:8000/api/webhook/save-stats/"
payload = {
    "energyOptimizationData": {
        "summary": {
            "total_consumption": 150.5,
            "anomalies": True,
            "average_power": 450.2
        },
        "statistics": {
            "voltage": {
                "min": 210,
                "max": 230,
                "average": 220
            }
        }
    },
    "wasteTrackingData": {
        "avgFill": 75.5,
        "criticalCount": 3,
        "warningCount": 5,
        "warningLocations": ["Point A", "Point B"]
    }
}

response = requests.post(url, json=payload)
print(response.json())
```

**Postman:**

-   Method: `POST`
-   URL: `http://localhost:8000/api/webhook/save-stats/`
-   Headers: `Content-Type: application/json`
-   Body (raw JSON):

```json
{
	"energyOptimizationData": {
		"summary": {
			"total_consumption": 150.5,
			"anomalies": true,
			"average_power": 450.2
		},
		"statistics": {
			"voltage": {
				"min": 210,
				"max": 230,
				"average": 220
			}
		}
	},
	"wasteTrackingData": {
		"avgFill": 75.5,
		"criticalCount": 3,
		"warningCount": 5,
		"warningLocations": ["Point A", "Point B"]
	}
}
```

### Response Example

**Success (201 Created):**

```json
{
	"success": true,
	"message": "Statistics saved successfully",
	"saved_records": {
		"energy_log_id": 1,
		"waste_log_id": 1
	}
}
```

**Error (400 Bad Request):**

```json
{
	"error": "Invalid data format",
	"details": {
		"energyOptimizationData": {
			"summary": {
				"total_consumption": ["This field is required."]
			}
		}
	}
}
```

### Notes

-   Both `energyOptimizationData` and `wasteTrackingData` are optional
-   If only one is provided, only one record will be created
-   Uses `transaction.atomic()` to ensure both logs save or neither saves
-   If transaction fails, no records are created

---

## 2. Dashboard Data Endpoint

### Endpoint

```
GET /api/dashboard/
```

### Purpose

Provides comprehensive dashboard data for frontend visualization including latest traffic, energy, waste stats and citizen reports.

### Request Example

**cURL:**

```bash
curl -X GET http://localhost:8000/api/dashboard/
```

**Python (requests):**

```python
import requests

url = "http://localhost:8000/api/dashboard/"
response = requests.get(url)
print(response.json())
```

**JavaScript (fetch):**

```javascript
fetch('http://localhost:8000/api/dashboard/')
	.then((response) => response.json())
	.then((data) => console.log(data))
	.catch((error) => console.error('Error:', error));
```

### Response Example

**Success (200 OK) - With Data:**

```json
{
	"traffic": {
		"id": 1,
		"address": "Phan Chau Trinh, Da Nang",
		"congestion_rate": 0.21,
		"flow_speed": 22,
		"delay_time": 7,
		"has_incident": true,
		"incident_count": 5,
		"status_code": "HEAVY",
		"status_color": "#e74c3c",
		"analysis": "Nhiều sự cố được báo cáo gây cản trở giao thông",
		"recommendation": "Cẩn trọng khi di chuyển",
		"alternative_routes": ["Đường Hùng Vương", "Đường Lê Đình Dương"],
		"alert_content": "THÔNG BÁO GIAO THÔNG...",
		"created_at": "2025-12-25T10:30:00Z"
	},
	"energy": {
		"id": 1,
		"total_consumption": 150.5,
		"avg_power": 450.2,
		"voltage_stats": {
			"min": 210,
			"max": 230,
			"average": 220
		},
		"anomalies_detected": true,
		"created_at": "2025-12-25T10:30:00Z"
	},
	"waste": {
		"id": 1,
		"avg_fill_level": 75.5,
		"critical_count": 3,
		"warning_count": 5,
		"warning_locations": ["Point A", "Point B"],
		"created_at": "2025-12-25T10:30:00Z"
	},
	"reports": {
		"pending_count": 5,
		"total_count": 12,
		"recent": [
			{
				"id": 1,
				"reporter_name": "Nguyen Van A",
				"issue_type": "traffic",
				"issue_type_display": "Traffic Issue",
				"description": "Traffic light not working",
				"image": null,
				"location": "123 Main Street",
				"status": "pending",
				"status_display": "Pending Review",
				"created_at": "2025-12-25T10:00:00Z",
				"updated_at": "2025-12-25T10:00:00Z"
			}
		]
	}
}
```

**Success (200 OK) - Empty Database (First Run):**

```json
{
	"traffic": null,
	"energy": null,
	"waste": null,
	"reports": {
		"pending_count": 0,
		"total_count": 0,
		"recent": []
	}
}
```

### Notes

-   Returns `null` for sections with no data (no DoesNotExist errors)
-   Always returns `reports` section even if empty
-   `pending_count` shows number of reports with status="pending"
-   `recent` shows up to 5 most recent reports of any status
-   Frontend should check for `null` values before rendering

---

## 3. Traffic Analysis Endpoint

### Endpoint

```
POST /api/check-traffic/
```

### Purpose

Analyzes traffic at a specific location via n8n webhook.

### Request Example

**cURL:**

```bash
curl -X POST http://localhost:8000/api/check-traffic/ \
  -H "Content-Type: application/json" \
  -d '{"location": "Phan Chau Trinh, Da Nang"}'
```

### Response Example

```json
{
	"address": "Phan Chau Trinh, Da Nang",
	"congestionRate": 0.21,
	"hasIncident": true,
	"incidentCount": 5,
	"flowSpeed": 22,
	"delayTime": 7,
	"statusCode": "HEAVY",
	"statusColor": "#e74c3c",
	"analysis": "Nhiều sự cố được báo cáo",
	"recommendation": "Cẩn trọng khi di chuyển",
	"alternativeRoutes": ["Đường Hùng Vương"],
	"alert_content": "THÔNG BÁO GIAO THÔNG..."
}
```

---

## 4. Citizen Reports Endpoints

### Create Report

```
POST /api/reports/create/
```

**Request:**

```bash
curl -X POST http://localhost:8000/api/reports/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "reporter_name": "Nguyen Van A",
    "issue_type": "traffic",
    "description": "Traffic light malfunction at intersection",
    "location": "123 Main Street, Da Nang"
  }'
```

**Response (201 Created):**

```json
{
	"id": 1,
	"reporter_name": "Nguyen Van A",
	"issue_type": "traffic",
	"issue_type_display": "Traffic Issue",
	"description": "Traffic light malfunction at intersection",
	"image": null,
	"location": "123 Main Street, Da Nang",
	"status": "pending",
	"status_display": "Pending Review",
	"created_at": "2025-12-25T10:00:00Z",
	"updated_at": "2025-12-25T10:00:00Z"
}
```

### List Reports

```
GET /api/reports/
```

**Optional Query Parameters:**

-   `status` - Filter by status (pending, in_progress, resolved, rejected)
-   `issue_type` - Filter by type (traffic, waste, energy, other)

**Examples:**

```bash
# All reports
curl http://localhost:8000/api/reports/

# Only pending reports
curl http://localhost:8000/api/reports/?status=pending

# Only traffic issues
curl http://localhost:8000/api/reports/?issue_type=traffic

# Pending traffic issues
curl http://localhost:8000/api/reports/?status=pending&issue_type=traffic
```

---

## Error Handling

### Common Error Responses

**400 Bad Request:**

```json
{
	"error": "Invalid data format",
	"details": {
		"field_name": ["Error message"]
	}
}
```

**500 Internal Server Error:**

```json
{
	"error": "Failed to fetch dashboard data",
	"details": "Specific error message"
}
```

**503 Service Unavailable:**

```json
{
	"error": "Traffic analysis service not configured"
}
```

---

## Testing Workflow

### 1. Test n8n Webhook (Save Stats)

```bash
# Send energy and waste data
curl -X POST http://localhost:8000/api/webhook/save-stats/ \
  -H "Content-Type: application/json" \
  -d '{
    "energyOptimizationData": {
      "summary": {"total_consumption": 150.5, "anomalies": true, "average_power": 450.2},
      "statistics": {"voltage": {"min": 210, "max": 230, "average": 220}}
    },
    "wasteTrackingData": {
      "avgFill": 75.5,
      "criticalCount": 3,
      "warningCount": 5,
      "warningLocations": ["Point A", "Point B"]
    }
  }'
```

### 2. Test Traffic Analysis

```bash
curl -X POST http://localhost:8000/api/check-traffic/ \
  -H "Content-Type: application/json" \
  -d '{"location": "Phan Chau Trinh, Da Nang"}'
```

### 3. Create Some Citizen Reports

```bash
curl -X POST http://localhost:8000/api/reports/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "reporter_name": "Test User",
    "issue_type": "waste",
    "description": "Overflowing trash bin",
    "location": "Park Avenue"
  }'
```

### 4. View Dashboard

```bash
curl http://localhost:8000/api/dashboard/
```

You should see all the data combined in one response!

---

## Integration with n8n

### n8n Webhook Configuration

**For Save Stats Webhook:**

1. Create HTTP Request node in n8n
2. Method: POST
3. URL: `http://your-server:8000/api/webhook/save-stats/`
4. Body: JSON with energyOptimizationData and wasteTrackingData
5. Schedule with Cron or Interval node

**For Traffic Analysis Webhook:**

1. Django makes request TO n8n
2. Configure `N8N_TRAFFIC_WEBHOOK` environment variable
3. n8n returns traffic analysis data
4. Django saves and returns to frontend

---

## Database Schema Summary

### EnergyLog

-   `total_consumption` (Float)
-   `avg_power` (Float)
-   `voltage_stats` (JSON: {min, max, average})
-   `anomalies_detected` (Boolean)

### WasteLog

-   `avg_fill_level` (Float)
-   `critical_count` (Integer)
-   `warning_count` (Integer)
-   `warning_locations` (JSON Array)

### TrafficLog

-   `address` (String)
-   `congestion_rate`, `flow_speed`, `delay_time`
-   `has_incident`, `incident_count`
-   `status_code`, `status_color`
-   `analysis`, `recommendation`, `alternative_routes`, `alert_content`

### CitizenReport

-   `reporter_name`, `issue_type`, `description`
-   `location`, `status`, `image`
