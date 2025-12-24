"""
Serializers for Smart City API models.
"""

from rest_framework import serializers
from .models import TrafficLog, EnergyLog, WasteLog, CitizenReport


class TrafficLogSerializer(serializers.ModelSerializer):
    """Serializer for TrafficLog model."""

    class Meta:
        model = TrafficLog
        fields = [
            "id",
            "address",
            "congestion_rate",
            "flow_speed",
            "delay_time",
            "has_incident",
            "incident_count",
            "status_code",
            "status_color",
            "analysis",
            "recommendation",
            "alternative_routes",
            "alert_content",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class EnergyLogSerializer(serializers.ModelSerializer):
    """Serializer for EnergyLog model."""

    class Meta:
        model = EnergyLog
        fields = [
            "id",
            "total_consumption",
            "avg_power",
            "voltage_stats",
            "anomalies_detected",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class WasteLogSerializer(serializers.ModelSerializer):
    """Serializer for WasteLog model."""

    class Meta:
        model = WasteLog
        fields = [
            "id",
            "avg_fill_level",
            "critical_count",
            "warning_count",
            "warning_locations",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CitizenReportSerializer(serializers.ModelSerializer):
    """Serializer for CitizenReport model."""

    # Make issue_type and status human-readable in responses
    issue_type_display = serializers.CharField(
        source="get_issue_type_display", read_only=True
    )
    status_display = serializers.CharField(source="get_status_display", read_only=True)

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
            "status",
            "status_display",
            "created_at",
            "updated_at",
        ]


class CheckTrafficRequestSerializer(serializers.Serializer):
    """Serializer for check-traffic request payload."""

    location = serializers.CharField(max_length=255, required=True)


class N8NWebhookDataSerializer(serializers.Serializer):
    """
    Serializer for incoming n8n webhook data.
    Handles energyOptimizationData and wasteTrackingData.
    """

    class EnergyOptimizationDataSerializer(serializers.Serializer):
        """Nested serializer for energy data."""

        class SummarySerializer(serializers.Serializer):
            total_consumption = serializers.FloatField()
            anomalies = serializers.BooleanField(default=False)
            average_power = serializers.FloatField()

        class StatisticsSerializer(serializers.Serializer):
            class VoltageSerializer(serializers.Serializer):
                min = serializers.FloatField()
                max = serializers.FloatField()
                average = serializers.FloatField()

            voltage = VoltageSerializer()

        summary = SummarySerializer()
        statistics = StatisticsSerializer()

    class WasteTrackingDataSerializer(serializers.Serializer):
        """Nested serializer for waste data."""

        avgFill = serializers.FloatField()
        criticalCount = serializers.IntegerField()
        warningCount = serializers.IntegerField()
        warningLocations = serializers.ListField(
            child=serializers.CharField(), allow_empty=True
        )

    energyOptimizationData = EnergyOptimizationDataSerializer(required=False)
    wasteTrackingData = WasteTrackingDataSerializer(required=False)


class DashboardResponseSerializer(serializers.Serializer):
    """Serializer for dashboard response data."""

    traffic = TrafficLogSerializer(allow_null=True)
    energy = EnergyLogSerializer(allow_null=True)
    waste = WasteLogSerializer(allow_null=True)
    reports = serializers.DictField()
