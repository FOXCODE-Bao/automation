"""
URL Configuration for Smart City API endpoints.
"""

from django.urls import path
from .views import (
    CheckTrafficView,
    SaveStatsWebhookView,
    DashboardView,
    CitizenReportCreateView,
    CitizenReportListView,
)

app_name = "api"

urlpatterns = [
    # Traffic analysis endpoint
    path("check-traffic/", CheckTrafficView.as_view(), name="check-traffic"),
    # n8n webhook receiver
    path("webhook/save-stats/", SaveStatsWebhookView.as_view(), name="save-stats"),
    # Dashboard data
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    # Citizen reports
    path("reports/", CitizenReportListView.as_view(), name="report-list"),
    path("reports/create/", CitizenReportCreateView.as_view(), name="report-create"),
]
