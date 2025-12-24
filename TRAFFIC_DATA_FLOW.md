# Traffic Analysis Data Flow

## Overview

This document explains how traffic analysis data is collected, stored, and can be accessed in the Smart City Backend.

## Data Flow Diagram

```
User/Frontend
    ↓ (POST request with location)
CheckTrafficView (/api/check-traffic/)
    ↓ (forwards to n8n)
n8n Workflow (traffic analysis)
    ↓ (returns analysis results)
CheckTrafficView
    ↓ (saves to database)
PostgreSQL Database (TrafficAnalysis model)
    ↓ (can be viewed via)
Django Admin Panel / API Queries
```

## API Request Example

### Endpoint

`POST /api/check-traffic/`

### Request Body

```json
{
	"location": "Le Van Hien, Ngu Hanh Son, Da Nang"
}
```

### Response Body

```json
{
	"success": true,
	"data": {
		"address": "Le Van Hien, Ngu Hanh Son, Da Nang",
		"congestionRate": 0,
		"hasIncident": false,
		"incidentCount": 0,
		"flowSpeed": 49,
		"delayTime": 0,
		"statusCode": "CLEAR",
		"statusColor": "#2ecc71",
		"analysis": "Giao thông thông suốt, tốc độ di chuyển tối ưu.",
		"recommendation": "Tiếp tục di chuyển theo lộ trình, không có vấn đề gì.",
		"alternativeRoutes": ["Đường Nam Kỳ Khởi Nghĩa", "Đường Mai Đăng Chơn"],
		"alert_content": "THÔNG BÁO GIAO THÔNG..."
	},
	"message": "Traffic analysis completed"
}
```

## Database Schema

### TrafficAnalysis Table

| Field              | Type         | Description                                         |
| ------------------ | ------------ | --------------------------------------------------- |
| id                 | Integer (PK) | Auto-incrementing primary key                       |
| address            | String(500)  | Full address of the analyzed location               |
| congestion_rate    | Float        | Traffic congestion rate (0-1)                       |
| has_incident       | Boolean      | Whether there are incidents                         |
| incident_count     | Integer      | Number of incidents detected                        |
| flow_speed         | Integer      | Traffic flow speed in km/h                          |
| delay_time         | Integer      | Delay time in minutes                               |
| status_code        | String(20)   | Status code (CLEAR, LIGHT, MODERATE, HEAVY, SEVERE) |
| status_color       | String(20)   | Hex color code for visualization                    |
| analysis           | Text         | Vietnamese analysis description                     |
| recommendation     | Text         | Vietnamese recommendation text                      |
| alternative_routes | JSON         | Array of alternative route names                    |
| alert_content      | Text         | Full alert notification content                     |
| created_at         | DateTime     | Timestamp when record was created                   |

### Indexes

-   Primary index on `created_at` (DESC) and `status_code`
-   Secondary index on `address` and `created_at` (DESC)

## Implementation Details

### Model Definition

See [api/models.py](api/models.py) - `TrafficAnalysis` class

### View Logic

See [api/views.py](api/views.py) - `CheckTrafficView` class

The view performs these steps:

1. Validates the incoming location request
2. Calls n8n webhook for traffic analysis
3. Receives and parses the response
4. **Automatically saves the data** to PostgreSQL using `TrafficAnalysis.objects.create()`
5. Returns the response to the frontend

### Auto-save Implementation

```python
# Extract data from n8n response
if n8n_data.get("success") and "data" in n8n_data:
    analysis_data = n8n_data["data"]

    # Save to database
    traffic_analysis = TrafficAnalysis.objects.create(
        address=analysis_data.get("address", location),
        congestion_rate=analysis_data.get("congestionRate", 0.0),
        has_incident=analysis_data.get("hasIncident", False),
        # ... other fields
    )
```

## Querying the Data

### Via Django ORM

```python
from api.models import TrafficAnalysis

# Get all analyses
all_analyses = TrafficAnalysis.objects.all()

# Get recent analyses for a location
recent = TrafficAnalysis.objects.filter(
    address__icontains="Le Van Hien"
).order_by('-created_at')[:10]

# Get analyses with incidents
incidents = TrafficAnalysis.objects.filter(has_incident=True)

# Get by status
heavy_traffic = TrafficAnalysis.objects.filter(status_code='HEAVY')
```

### Via Django Admin

1. Navigate to: `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Click on "Traffic Analyses"
4. View, filter, and search through all saved records

### Via REST API (Future Enhancement)

You could create a new view to retrieve historical data:

```python
# In views.py
class TrafficAnalysisListView(generics.ListAPIView):
    queryset = TrafficAnalysis.objects.all()
    serializer_class = TrafficAnalysisSerializer

# In urls.py
path("traffic-history/", TrafficAnalysisListView.as_view(), name="traffic-history"),
```

## Status Codes

| Code     | Description         | Typical Color         |
| -------- | ------------------- | --------------------- |
| CLEAR    | No congestion       | #2ecc71 (Green)       |
| LIGHT    | Light traffic       | #3498db (Blue)        |
| MODERATE | Moderate congestion | #f39c12 (Orange)      |
| HEAVY    | Heavy traffic       | #e67e22 (Dark Orange) |
| SEVERE   | Severe congestion   | #e74c3c (Red)         |

## Usage Example

### 1. Make API Call

```bash
curl -X POST http://localhost:8000/api/check-traffic/ \
  -H "Content-Type: application/json" \
  -d '{"location": "Le Van Hien, Ngu Hanh Son, Da Nang"}'
```

### 2. Data is Automatically Saved

The response is saved to PostgreSQL with all fields populated.

### 3. View in Admin Panel

```bash
# Access admin
http://localhost:8000/admin/api/trafficanalysis/

# You'll see all saved analyses with:
# - Address
# - Status code
# - Congestion rate
# - Flow speed
# - Incident count
# - Timestamp
```

## Testing

### Check if Data is Being Saved

```bash
# Using Django shell
python manage.py shell

>>> from api.models import TrafficAnalysis
>>> TrafficAnalysis.objects.count()
5  # Shows number of records

>>> latest = TrafficAnalysis.objects.first()
>>> print(latest.address)
'Le Van Hien, Ngu Hanh Son, Da Nang'

>>> print(latest.status_code)
'CLEAR'
```

### Check Database Directly

```bash
# Using PostgreSQL
python manage.py dbshell

SELECT id, address, status_code, flow_speed, created_at
FROM api_trafficanalysis
ORDER BY created_at DESC
LIMIT 5;
```

## Error Handling

If saving fails:

-   Error is logged: `logger.error(f"Failed to save TrafficAnalysis: {save_error}")`
-   API continues to return response to frontend
-   Data is not lost, just not stored in database

Check logs for errors:

```bash
# In Django console output
Failed to save TrafficAnalysis: <error message>
```

## Performance Considerations

-   Database saves are synchronous but fast (~10-50ms)
-   Indexes on `created_at` ensure fast queries for recent data
-   JSON fields store alternative routes efficiently
-   Consider adding pagination for large datasets

## Future Enhancements

1. **Historical API endpoint** - Query past analyses
2. **Analytics dashboard** - Aggregate statistics
3. **Real-time notifications** - Alert on incidents
4. **Data retention policy** - Archive old data
5. **Caching layer** - Redis for frequently accessed data
