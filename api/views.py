"""
API Views for Smart City Backend with n8n integration.
"""

import os
import logging
import requests
from django.db import transaction
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

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
    then saves to EnergyLog and WasteLog.
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
            with transaction.atomic():
                # Save Energy data if present
                if "energyOptimizationData" in validated_data:
                    energy_data = validated_data["energyOptimizationData"]
                    energy_log = EnergyLog.objects.create(
                        total_consumption=energy_data["total_consumption"],
                        avg_power=energy_data["avg_power"],
                        voltage_stats=energy_data["voltage_stats"],
                        anomalies_detected=energy_data.get("anomalies_detected", False),
                    )
                    saved_records["energy_log_id"] = energy_log.id
                    logger.info(f"Created EnergyLog: {energy_log.id}")

                # Save Waste data if present
                if "wasteTrackingData" in validated_data:
                    waste_data = validated_data["wasteTrackingData"]
                    waste_log = WasteLog.objects.create(
                        avg_fill_level=waste_data["avg_fill_level"],
                        critical_count=waste_data["critical_count"],
                        warning_count=waste_data["warning_count"],
                        warning_locations=waste_data["warning_locations"],
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
                {"error": "Failed to save statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DashboardView(APIView):
    """
    GET /api/dashboard/

    Returns the latest record from TrafficLog, EnergyLog, and WasteLog
    for dashboard display.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        try:
            # Efficient queries - get only the latest record from each table
            latest_traffic = TrafficLog.objects.order_by("-created_at").first()
            latest_energy = EnergyLog.objects.order_by("-created_at").first()
            latest_waste = WasteLog.objects.order_by("-created_at").first()

            # Serialize data
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
                "timestamp": request.build_absolute_uri(),  # Current request time
            }

            return Response(dashboard_data, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Dashboard view error: {str(e)}")
            return Response(
                {"error": "Failed to fetch dashboard data"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CitizenReportCreateView(generics.CreateAPIView):
    """
    POST /api/reports/

    Standard CreateAPIView for citizens to submit reports.
    Optionally triggers n8n webhook after creation.
    """

    queryset = CitizenReport.objects.all()
    serializer_class = CitizenReportSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Save the report
        report = serializer.save()
        logger.info(f"Created CitizenReport: {report.id}")

        # Optional: Trigger n8n webhook for notifications
        n8n_report_webhook = os.environ.get("N8N_REPORT_WEBHOOK")
        if n8n_report_webhook:
            try:
                report_data = {
                    "report_id": report.id,
                    "reporter_name": report.reporter_name,
                    "issue_type": report.issue_type,
                    "location": report.location,
                    "description": report.description,
                    "status": report.status,
                    "created_at": report.created_at.isoformat(),
                }

                # Non-blocking webhook call (fire and forget)
                requests.post(n8n_report_webhook, json=report_data, timeout=5)
                logger.info(f"Triggered n8n webhook for report {report.id}")
            except Exception as e:
                # Log but don't fail the request
                logger.warning(f"Failed to trigger n8n webhook for report: {str(e)}")


class CitizenReportListView(generics.ListAPIView):
    """
    GET /api/reports/

    List all citizen reports with optional filtering.
    """

    queryset = CitizenReport.objects.all().order_by("-created_at")
    serializer_class = CitizenReportSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()

        # Optional filtering by status
        status_filter = self.request.query_params.get("status", None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Optional filtering by issue_type
        issue_type = self.request.query_params.get("issue_type", None)
        if issue_type:
            queryset = queryset.filter(issue_type=issue_type)

        return queryset
