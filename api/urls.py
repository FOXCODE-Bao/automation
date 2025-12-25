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
    SubscribeView,
    SubscriberListView,
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
    # Newsletter subscription
    path("subscribe/", SubscribeView.as_view(), name="subscribe"),
    # Subscriber list for n8n email automation
    path("subscribers/", SubscriberListView.as_view(), name="subscribers"),
    # Include router URLs for CitizenReport ViewSet
    path("", include(router.urls)),
]
