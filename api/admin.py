from django.contrib import admin
from .models import TrafficLog, EnergyLog, WasteLog, CitizenReport


@admin.register(TrafficLog)
class TrafficLogAdmin(admin.ModelAdmin):
    list_display = [
        "address",
        "status_code",
        "congestion_rate",
        "flow_speed",
        "incident_count",
        "created_at",
    ]
    list_filter = ["status_code", "has_incident", "created_at"]
    search_fields = ["address", "analysis", "recommendation"]
    readonly_fields = ["created_at"]
    ordering = ["-created_at"]

    fieldsets = (
        (
            "Location",
            {
                "fields": ("address",),
            },
        ),
        (
            "Traffic Metrics",
            {
                "fields": (
                    "congestion_rate",
                    "flow_speed",
                    "delay_time",
                    "has_incident",
                    "incident_count",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": ("status_code", "status_color"),
            },
        ),
        (
            "Analysis & Recommendations",
            {
                "fields": ("analysis", "recommendation", "alternative_routes"),
            },
        ),
        (
            "Alerts",
            {
                "fields": ("alert_content",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at",),
            },
        ),
    )


@admin.register(EnergyLog)
class EnergyLogAdmin(admin.ModelAdmin):
    list_display = [
        "total_consumption",
        "avg_power",
        "anomalies_detected",
        "created_at",
    ]
    list_filter = ["anomalies_detected", "created_at"]
    readonly_fields = ["created_at"]


@admin.register(WasteLog)
class WasteLogAdmin(admin.ModelAdmin):
    list_display = ["avg_fill_level", "critical_count", "warning_count", "created_at"]
    list_filter = ["created_at"]
    readonly_fields = ["created_at"]


@admin.register(CitizenReport)
class CitizenReportAdmin(admin.ModelAdmin):
    list_display = ["reporter_name", "issue_type", "location", "status", "created_at"]
    list_filter = ["issue_type", "status", "created_at"]
    search_fields = ["reporter_name", "location", "description"]
    readonly_fields = ["created_at", "updated_at"]
