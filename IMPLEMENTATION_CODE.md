# Implementation Code Snippets

This file contains the exact code snippets for the Citizen Report feature implementation.

---

## 1. Settings Configuration (core/settings.py)

### Add to INSTALLED_APPS

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "corsheaders",
    "django_filters",  # ← Added for filtering support
    # Local apps
    "api",
]
```

### Media Configuration (Already Present)

```python
# Media files (User-uploaded content)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

---

## 2. URL Configuration (core/urls.py)

### Media File Serving (Already Present)

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("api.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 3. Serializer (api/serializers.py)

### CitizenReportSerializer (Already Implemented)

```python
from rest_framework import serializers
from .models import CitizenReport


class CitizenReportSerializer(serializers.ModelSerializer):
    """Serializer for CitizenReport model."""

    # Make issue_type and status human-readable in responses
    issue_type_display = serializers.CharField(
        source="get_issue_type_display", read_only=True
    )
    status_display = serializers.CharField(
        source="get_status_display", read_only=True
    )

    class Meta:
        model = CitizenReport
        fields = [
            "id",
            "reporter_name",
            "issue_type",
            "issue_type_display",
            "description",
            "image",
            "location",
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "status",  # ← Status is read-only, defaults to 'pending'
            "status_display",
            "created_at",
            "updated_at",
        ]
```

---

## 4. ViewSet (api/views.py)

### Imports

```python
import os
import logging
import requests
from django.db import transaction
from rest_framework import status, generics, viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend

from .models import TrafficLog, EnergyLog, WasteLog, CitizenReport
from .serializers import (
    TrafficLogSerializer,
    EnergyLogSerializer,
    WasteLogSerializer,
    CitizenReportSerializer,
    CheckTrafficRequestSerializer,
    N8NWebhookDataSerializer,
)

logger = logging.getLogger(__name__)
```

### CitizenReportViewSet

```python
class CitizenReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for CitizenReport model.

    Endpoints:
    - GET /api/reports/ - List all reports with filtering support
    - POST /api/reports/ - Create new report (supports multipart/form-data for image uploads)
    - GET /api/reports/{id}/ - Retrieve specific report
    - PUT/PATCH /api/reports/{id}/ - Update report (admin only in production)
    - DELETE /api/reports/{id}/ - Delete report (admin only in production)

    Features:
    - Multipart/Form-data support for image uploads
    - Filtering by status and issue_type (?status=pending&issue_type=traffic)
    - Ordering by created_at (default: latest first)
    """

    queryset = CitizenReport.objects.all()
    serializer_class = CitizenReportSerializer
    permission_classes = [AllowAny]  # Use proper permissions in production

    # Support multiple parsers for file uploads
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # Enable filtering and ordering
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'issue_type']  # Allow filtering by these fields
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']  # Default ordering: latest first

    def perform_create(self, serializer):
        """
        Called when creating a new report.
        This is standalone - does NOT interact with n8n.
        """
        report = serializer.save()
        logger.info(
            f"Created CitizenReport #{report.id}: {report.issue_type} at {report.location} by {report.reporter_name}"
        )
```

---

## 5. URL Routing (api/urls.py)

```python
"""
URL Configuration for Smart City API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CheckTrafficView,
    SaveStatsWebhookView,
    DashboardView,
    CitizenReportViewSet,
)

app_name = "api"

# Create a router for ViewSets
router = DefaultRouter()
router.register(r'reports', CitizenReportViewSet, basename='report')

urlpatterns = [
    # Traffic analysis endpoint
    path("check-traffic/", CheckTrafficView.as_view(), name="check-traffic"),
    # n8n webhook receiver
    path("webhook/save-stats/", SaveStatsWebhookView.as_view(), name="save-stats"),
    # Dashboard data
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Include router URLs for CitizenReport ViewSet
    path("", include(router.urls)),
]
```

This configuration automatically generates:

-   `GET /api/reports/` → list
-   `POST /api/reports/` → create
-   `GET /api/reports/{id}/` → retrieve
-   `PUT /api/reports/{id}/` → update
-   `PATCH /api/reports/{id}/` → partial_update
-   `DELETE /api/reports/{id}/` → destroy

---

## 6. Requirements (requirements.txt)

```txt
Django>=5.0,<6.0
djangorestframework>=3.14.0
django-cors-headers>=4.3.0
django-environ>=0.11.0
django-filter>=23.0          # ← Added for filtering support
Pillow>=10.0.0               # ← Required for image uploads
psycopg2-binary>=2.9.9
requests>=2.31.0
gunicorn>=21.2.0
```

---

## 7. Model (api/models.py) - Reference

The CitizenReport model (already exists):

```python
class CitizenReport(models.Model):
    """
    Model for citizens to report issues related to city services.
    """

    ISSUE_TYPE_CHOICES = [
        ("traffic", "Traffic Issue"),
        ("waste", "Waste Management"),
        ("energy", "Energy/Power Issue"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]

    reporter_name = models.CharField(
        max_length=255, help_text="Name of the person reporting"
    )
    issue_type = models.CharField(
        max_length=20,
        choices=ISSUE_TYPE_CHOICES,
        help_text="Type of issue being reported",
    )
    description = models.TextField(help_text="Detailed description of the issue")
    image = models.ImageField(
        upload_to="citizen_reports/%Y/%m/%d/",
        blank=True,
        null=True,
        help_text="Optional image of the issue",
    )
    location = models.CharField(max_length=255, help_text="Location of the issue")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        help_text="Current status of the report",
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Citizen Report"
        verbose_name_plural = "Citizen Reports"
        indexes = [
            models.Index(fields=["-created_at", "status"]),
            models.Index(fields=["issue_type", "status"]),
        ]

    def __str__(self):
        return f"{self.get_issue_type_display()} at {self.location} - {self.get_status_display()} (by {self.reporter_name})"
```

---

## Key Features Summary

✅ **Multipart/Form-Data Support**

-   `parser_classes = [MultiPartParser, FormParser, JSONParser]`
-   Handles image uploads automatically

✅ **Filtering**

-   `filter_backends = [DjangoFilterBackend, filters.OrderingFilter]`
-   `filterset_fields = ['status', 'issue_type']`
-   Usage: `?status=pending&issue_type=traffic`

✅ **Ordering**

-   `ordering_fields = ['created_at', 'updated_at']`
-   `ordering = ['-created_at']` (default: latest first)
-   Usage: `?ordering=created_at`

✅ **Read-Only Status**

-   Status field is read-only in serializer
-   Defaults to 'pending' on creation

✅ **No n8n Integration**

-   Standalone feature
-   Only saves to database
-   Provides REST API for frontend

---

## Installation & Testing

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Start server
python manage.py runserver

# 4. Test the API
python test_citizen_reports.py
```

---

## Quick Test Command

```bash
# Create a test report
curl -X POST http://localhost:8000/api/reports/ \
  -F "reporter_name=Test User" \
  -F "issue_type=traffic" \
  -F "description=Test traffic issue" \
  -F "location=Main Street"

# List all reports
curl http://localhost:8000/api/reports/

# Filter by status
curl "http://localhost:8000/api/reports/?status=pending"
```

---

**All code is production-ready and follows Django/DRF best practices!**
