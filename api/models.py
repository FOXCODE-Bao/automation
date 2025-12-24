from django.db import models
from django.utils import timezone


class TrafficLog(models.Model):
    """
    Model to store traffic analysis history from n8n workflow.
    """

    STATUS_CODE_CHOICES = [
        ("CLEAR", "Clear Traffic"),
        ("LIGHT", "Light Traffic"),
        ("MODERATE", "Moderate Traffic"),
        ("HEAVY", "Heavy Traffic"),
        ("SEVERE", "Severe Traffic"),
    ]

    # Location info
    address = models.CharField(max_length=500, help_text="Full address of the location")

    # Traffic metrics
    congestion_rate = models.FloatField(
        help_text="Traffic congestion rate (0-1 or percentage)"
    )
    flow_speed = models.IntegerField(help_text="Traffic flow speed in km/h")
    delay_time = models.IntegerField(default=0, help_text="Delay time in minutes")

    # Incident info
    has_incident = models.BooleanField(
        default=False, help_text="Whether there are incidents"
    )
    incident_count = models.IntegerField(
        default=0, help_text="Number of incidents detected"
    )

    # Status
    status_code = models.CharField(
        max_length=20,
        choices=STATUS_CODE_CHOICES,
        help_text="Traffic status code",
    )
    status_color = models.CharField(
        max_length=20,
        help_text="Color code for status visualization",
    )

    # Analysis content
    analysis = models.TextField(help_text="Traffic analysis description")
    recommendation = models.TextField(help_text="Recommended actions")
    alternative_routes = models.JSONField(
        default=list, help_text="List of alternative route suggestions"
    )
    alert_content = models.TextField(blank=True, help_text="Alert notification content")

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Traffic Log"
        verbose_name_plural = "Traffic Logs"
        indexes = [
            models.Index(fields=["-created_at", "status_code"]),
            models.Index(fields=["address", "-created_at"]),
        ]

    def __str__(self):
        return f"Traffic: {self.address} - {self.status_code} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class EnergyLog(models.Model):
    """
    Model to store energy optimization statistics from n8n workflow.
    """

    total_consumption = models.FloatField(help_text="Total energy consumption in kWh")
    avg_power = models.FloatField(help_text="Average power usage in watts")
    voltage_stats = models.JSONField(
        default=dict, help_text="Voltage statistics (min, max, avg)"
    )
    anomalies_detected = models.BooleanField(
        default=False, help_text="Whether anomalies were detected"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Energy Log"
        verbose_name_plural = "Energy Logs"
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        anomaly_text = "⚠️ Anomalies" if self.anomalies_detected else "✓ Normal"
        return f"Energy Log - {self.total_consumption:.2f} kWh - {anomaly_text} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


class WasteLog(models.Model):
    """
    Model to store waste tracking data from n8n workflow.
    """

    avg_fill_level = models.FloatField(
        help_text="Average fill level percentage (0-100)"
    )
    critical_count = models.IntegerField(
        default=0, help_text="Number of bins at critical level"
    )
    warning_count = models.IntegerField(
        default=0, help_text="Number of bins at warning level"
    )
    warning_locations = models.JSONField(
        default=list, help_text="List of locations with warnings"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Waste Log"
        verbose_name_plural = "Waste Logs"
        indexes = [
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Waste Log - {self.avg_fill_level:.1f}% avg - {self.critical_count} critical ({self.created_at.strftime('%Y-%m-%d %H:%M')})"


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
