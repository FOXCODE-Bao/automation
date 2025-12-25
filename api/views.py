"""
API Views for Smart City Backend with n8n integration.
"""

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


class CheckTrafficView(APIView):
    """
    POST /api/check-traffic/

    Receives location, calls n8n webhook for traffic analysis,
    returns response immediately, and saves to TrafficLog.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        # Validate incoming request
        serializer = CheckTrafficRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Invalid request", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        location = serializer.validated_data["location"]
        n8n_webhook_url = os.environ.get("N8N_TRAFFIC_WEBHOOK")

        if not n8n_webhook_url:
            logger.error("N8N_TRAFFIC_WEBHOOK environment variable not set")
            return Response(
                {"error": "Traffic analysis service not configured"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            # Call n8n webhook with timeout
            logger.info(f"Calling n8n webhook for location: {location}")
            response = requests.post(
                n8n_webhook_url,
                json={"location": location},
                timeout=30,  # 30 second timeout
            )
            response.raise_for_status()

            # Parse n8n response
            n8n_data = response.json()
            logger.info(f"Received response from n8n: {n8n_data}")

            # Save traffic data to database
            try:
                traffic_log = TrafficLog.objects.create(
                    address=n8n_data.get("address", location),
                    congestion_rate=n8n_data.get("congestionRate", 0.0),
                    flow_speed=n8n_data.get("flowSpeed", 0),
                    delay_time=n8n_data.get("delayTime", 0),
                    has_incident=n8n_data.get("hasIncident", False),
                    incident_count=n8n_data.get("incidentCount", 0),
                    status_code=n8n_data.get("statusCode", "CLEAR"),
                    status_color=n8n_data.get("statusColor", "#2ecc71"),
                    analysis=n8n_data.get("analysis", ""),
                    recommendation=n8n_data.get("recommendation", ""),
                    alternative_routes=n8n_data.get("alternativeRoutes", []),
                    alert_content=n8n_data.get("alert_content", ""),
                )
                logger.info(f"Saved TrafficLog: {traffic_log.id}")
            except Exception as save_error:
                logger.error(f"Failed to save TrafficLog: {save_error}")
                # Continue even if save fails

            # Return n8n response to frontend
            return Response(
                n8n_data,
                status=status.HTTP_200_OK,
            )

        except requests.exceptions.Timeout:
            logger.error(f"n8n webhook timeout for location: {location}")
            return Response(
                {"error": "Traffic analysis service timeout"},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"n8n webhook request failed: {str(e)}")
            return Response(
                {"error": "Failed to connect to traffic analysis service"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Exception as e:
            logger.error(f"Unexpected error in check-traffic: {str(e)}")
            return Response(
                {"error": "Internal server error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class SaveStatsWebhookView(APIView):
    """
    POST /api/webhook/save-stats/

    Webhook receiver for n8n scheduled analysis.
    Receives energyOptimizationData and wasteTrackingData,
    then saves to EnergyLog and WasteLog using atomic transaction.

    Expected payload structure:
    {
        "energyOptimizationData": {
            "summary": { "total_consumption": 150.5, "anomalies": true, "average_power": 450.2 },
            "statistics": { "voltage": { "min": 210, "max": 230, "average": 220 } }
        },
        "wasteTrackingData": {
            "avgFill": 75.5,
            "criticalCount": 3,
            "warningCount": 5,
            "warningLocations": ["Point A", "Point B"]
        }
    }
    """

    permission_classes = [AllowAny]  # Add authentication for production

    def post(self, request):
        # Validate incoming data
        serializer = N8NWebhookDataSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(f"Invalid webhook data: {serializer.errors}")
            return Response(
                {"error": "Invalid data format", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        validated_data = serializer.validated_data
        saved_records = {}

        try:
            # Use atomic transaction to ensure both logs are saved or neither is
            with transaction.atomic():
                # Save Energy data if present
                if "energyOptimizationData" in validated_data:
                    energy_data = validated_data["energyOptimizationData"]
                    summary = energy_data["summary"]
                    voltage = energy_data["statistics"]["voltage"]

                    energy_log = EnergyLog.objects.create(
                        total_consumption=summary["total_consumption"],
                        avg_power=summary["average_power"],
                        voltage_stats={
                            "min": voltage["min"],
                            "max": voltage["max"],
                            "average": voltage["average"],
                        },
                        anomalies_detected=summary.get("anomalies", False),
                    )
                    saved_records["energy_log_id"] = energy_log.id
                    logger.info(f"Created EnergyLog: {energy_log.id}")

                # Save Waste data if present
                if "wasteTrackingData" in validated_data:
                    waste_data = validated_data["wasteTrackingData"]
                    waste_log = WasteLog.objects.create(
                        avg_fill_level=waste_data["avgFill"],
                        critical_count=waste_data["criticalCount"],
                        warning_count=waste_data["warningCount"],
                        warning_locations=waste_data["warningLocations"],
                    )
                    saved_records["waste_log_id"] = waste_log.id
                    logger.info(f"Created WasteLog: {waste_log.id}")

            return Response(
                {
                    "success": True,
                    "message": "Statistics saved successfully",
                    "saved_records": saved_records,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            logger.error(f"Failed to save stats from n8n webhook: {str(e)}")
            return Response(
                {"error": "Failed to save statistics", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DashboardView(APIView):
    """
    GET /api/dashboard/

    Returns comprehensive dashboard data including:
    - Latest TrafficLog record
    - Latest EnergyLog record
    - Latest WasteLog record
    - Count of pending CitizenReport records
    - 5 most recent CitizenReport records

    Handles empty tables gracefully by returning null/zero values.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Fetch latest records from each table (returns None if table is empty)
            latest_traffic = TrafficLog.objects.order_by("-created_at").first()
            latest_energy = EnergyLog.objects.order_by("-created_at").first()
            latest_waste = WasteLog.objects.order_by("-created_at").first()

            # Count pending citizen reports
            pending_reports_count = CitizenReport.objects.filter(
                status="pending"
            ).count()

            # Get 5 most recent citizen reports
            recent_reports = CitizenReport.objects.order_by("-created_at")[:5]

            # Build response data with null-safe handling
            dashboard_data = {
                "traffic": (
                    TrafficLogSerializer(latest_traffic).data
                    if latest_traffic
                    else None
                ),
                "energy": (
                    EnergyLogSerializer(latest_energy).data if latest_energy else None
                ),
                "waste": (
                    WasteLogSerializer(latest_waste).data if latest_waste else None
                ),
                "reports": {
                    "pending_count": pending_reports_count,
                    "recent": CitizenReportSerializer(recent_reports, many=True).data,
                    "total_count": CitizenReport.objects.count(),
                },
            }

            logger.info("Dashboard data fetched successfully")
            return Response(dashboard_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Dashboard view error: {str(e)}")
            return Response(
                {"error": "Failed to fetch dashboard data", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


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
