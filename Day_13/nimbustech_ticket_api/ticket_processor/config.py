"""Configuration constants for the ticket processing script."""

from pathlib import Path

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
INVALID_ROW_ABORT_RATIO = 0.10
PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3, "critical": 4}
REQUIRED_FIELDS = (
    "ticket_id",
    "customer_name",
    "category",
    "priority_raw",
    "created_at",
    "sla_hours",
    "status",
)
DEFAULT_OUTPUT_PATH = Path("data/tickets_report.json")
