"""Validation helpers for raw ticket CSV rows."""

from datetime import datetime

from .config import DATE_FORMAT, PRIORITY_SCORES, REQUIRED_FIELDS


def validate_ticket_row(ticket_row):
    """Validate a raw CSV ticket row.

    Args:
        ticket_row: Mapping produced by ``csv.DictReader``.

    Returns:
        tuple[bool, str | None]: Whether the row is valid and an error reason.
    """
    for field_name in REQUIRED_FIELDS:
        value = ticket_row.get(field_name)
        if value is None or not value.strip():
            return False, f"missing {field_name}"

    priority = ticket_row["priority_raw"].strip().lower()
    if priority not in PRIORITY_SCORES:
        return False, "invalid priority_raw"

    try:
        datetime.strptime(ticket_row["created_at"].strip(), DATE_FORMAT)
    except ValueError:
        return False, "invalid created_at"

    try:
        sla_hours = float(ticket_row["sla_hours"])
    except ValueError:
        return False, "invalid sla_hours"

    if sla_hours <= 0:
        return False, "sla_hours must be positive"

    return True, None
