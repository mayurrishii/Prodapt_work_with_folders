"""Configuration constants for the ticket API."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_ROOT / "data" / "tickets_report.json"
PRIORITY_SCORES = {"low": 1, "medium": 2, "high": 3, "critical": 4}
VALID_STATUSES = {"open", "in_progress", "resolved", "closed"}
CORS_ORIGINS = ["*"]
