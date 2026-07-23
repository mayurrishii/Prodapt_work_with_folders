"""CSV processing and JSON report construction for support tickets."""

import csv
from collections import Counter
from datetime import datetime, timedelta

from .config import DATE_FORMAT, PRIORITY_SCORES
from .models import Ticket
from .validators import validate_ticket_row


def row_to_text(ticket_row):
    """Convert a raw CSV row to a readable string.

    Args:
        ticket_row: Mapping produced by ``csv.DictReader``.

    Returns:
        str: Comma-separated raw row values.
    """
    return ",".join("" if value is None else value for value in ticket_row.values())


def create_ticket(ticket_row, current_time):
    """Create a classified ticket from an already validated row.

    Args:
        ticket_row: Valid raw ticket row.
        current_time: Timestamp used to determine SLA breaches.

    Returns:
        Ticket: Classified ticket object.
    """
    created_at = datetime.strptime(ticket_row["created_at"].strip(), DATE_FORMAT)
    sla_hours = float(ticket_row["sla_hours"])
    priority = ticket_row["priority_raw"].strip().lower()
    status = ticket_row["status"].strip().lower()
    sla_breached = created_at + timedelta(hours=sla_hours) < current_time
    sla_breached = sla_breached and status != "closed"

    return Ticket(
        ticket_id=ticket_row["ticket_id"].strip(),
        customer_name=ticket_row["customer_name"].strip(),
        category=ticket_row["category"].strip().lower(),
        priority_raw=priority,
        priority_score=PRIORITY_SCORES[priority],
        created_at=created_at,
        sla_hours=sla_hours,
        status=status,
        sla_breached=sla_breached,
    )


def process_csv(input_path, logger, current_time=None):
    """Read, validate, and classify tickets from a CSV file.

    Args:
        input_path: Path to the raw ticket CSV export.
        logger: Logger for operational messages.
        current_time: Optional timestamp for SLA calculations.

    Returns:
        tuple[list[Ticket], list[dict]]: Valid tickets and invalid row details.
    """
    valid_tickets = []
    invalid_rows = []
    processing_time = current_time or datetime.now()

    with open(input_path, encoding="utf-8", newline="") as input_file:
        reader = csv.DictReader(input_file)
        if reader.fieldnames is None:
            raise ValueError("input CSV is empty or has no header row")

        for row_number, ticket_row in enumerate(reader, start=2):
            is_valid, reason = validate_ticket_row(ticket_row)
            if not is_valid:
                invalid_rows.append({"raw_row": row_to_text(ticket_row), "reason": reason})
                logger.warning("Row %s skipped: %s", row_number, reason)
                continue

            valid_tickets.append(create_ticket(ticket_row, processing_time))

    logger.info("Rows read: %s", len(valid_tickets) + len(invalid_rows))
    return valid_tickets, invalid_rows


def build_report(valid_tickets, invalid_rows, generated_at=None):
    """Build the structured report for processed tickets.

    Args:
        valid_tickets: Classified valid tickets.
        invalid_rows: Invalid raw-row details.
        generated_at: Optional report creation timestamp.

    Returns:
        dict: JSON-serializable report with summary and ticket data.
    """
    categories = Counter(ticket.category for ticket in valid_tickets)
    total_rows = len(valid_tickets) + len(invalid_rows)
    breached_count = sum(ticket.sla_breached for ticket in valid_tickets)

    return {
        "generated_at": (generated_at or datetime.now()).isoformat(),
        "summary": {
            "total_rows": total_rows,
            "valid_tickets": len(valid_tickets),
            "invalid_rows": len(invalid_rows),
            "breached_count": breached_count,
            "by_category": dict(categories),
        },
        "tickets": [ticket.to_dict() for ticket in valid_tickets],
        "invalid_rows": invalid_rows,
    }
