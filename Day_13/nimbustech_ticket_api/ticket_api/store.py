"""In-memory storage loaded from the Module 1 ticket report."""

import json
import logging
from datetime import datetime, timedelta

from .config import PRIORITY_SCORES, REPORT_PATH

LOGGER = logging.getLogger(__name__)


class TicketStore:
    """Hold ticket report data in memory for the API lifetime."""

    def __init__(self):
        """Initialize an empty ticket store."""
        self.tickets = []
        self.invalid_rows = []

    def load_report(self, report_path=REPORT_PATH):
        """Load a Module 1 JSON report into memory.

        Args:
            report_path: Path to the generated ticket report.

        Returns:
            None
        """
        try:
            with open(report_path, encoding="utf-8") as report_file:
                report = json.load(report_file)
        except (OSError, json.JSONDecodeError) as error:
            LOGGER.error("Could not load ticket report %s: %s", report_path, error)
            self.tickets = []
            self.invalid_rows = []
            return

        self.tickets = report.get("tickets", [])
        self.invalid_rows = report.get("invalid_rows", [])
        LOGGER.info("Loaded %s tickets from %s", len(self.tickets), report_path)

    def get_ticket(self, ticket_id):
        """Find a ticket by identifier.

        Args:
            ticket_id: Ticket identifier to find.

        Returns:
            dict | None: Matching ticket, if present.
        """
        return next(
            (ticket for ticket in self.tickets if ticket["ticket_id"] == ticket_id),
            None,
        )

    def get_summary(self):
        """Calculate summary counts for the current in-memory tickets.

        Returns:
            dict: Current ticket summary.
        """
        category_counts = {}
        for ticket in self.tickets:
            category = ticket["category"]
            category_counts[category] = category_counts.get(category, 0) + 1

        return {
            "total_rows": len(self.tickets) + len(self.invalid_rows),
            "valid_tickets": len(self.tickets),
            "invalid_rows": len(self.invalid_rows),
            "breached_count": sum(ticket["sla_breached"] for ticket in self.tickets),
            "by_category": category_counts,
        }

    def create_ticket(self, ticket_data):
        """Create and store a ticket from validated request data.

        Args:
            ticket_data: Validated data from a ``TicketCreate`` model.

        Returns:
            dict: Newly stored ticket.
        """
        created_at = datetime.now()
        ticket = {
            "ticket_id": self._next_ticket_id(),
            "customer_name": ticket_data.customer_name,
            "category": ticket_data.category.lower(),
            "priority_raw": ticket_data.priority_raw,
            "priority_score": PRIORITY_SCORES[ticket_data.priority_raw],
            "created_at": created_at.isoformat(),
            "sla_hours": ticket_data.sla_hours,
            "status": ticket_data.status,
            "sla_breached": False,
        }
        ticket["sla_breached"] = self._is_sla_breached(ticket)
        self.tickets.append(ticket)
        return ticket

    def update_ticket(self, ticket, ticket_data):
        """Update the allowed fields of an existing ticket.

        Args:
            ticket: Stored ticket to update.
            ticket_data: Validated data from a ``TicketUpdate`` model.

        Returns:
            dict: Updated ticket.
        """
        changes = ticket_data.model_dump(exclude_none=True)
        ticket.update(changes)
        if "priority_raw" in changes:
            ticket["priority_score"] = PRIORITY_SCORES[ticket["priority_raw"]]
        ticket["sla_breached"] = self._is_sla_breached(ticket)
        return ticket

    def delete_ticket(self, ticket):
        """Remove a ticket from the store.

        Args:
            ticket: Stored ticket to remove.

        Returns:
            None
        """
        self.tickets.remove(ticket)

    def _next_ticket_id(self):
        """Generate the next sequential NimbusTech ticket ID.

        Returns:
            str: New unique ticket identifier.
        """
        numeric_ids = []
        for ticket in self.tickets:
            ticket_id = ticket.get("ticket_id", "")
            if ticket_id.startswith("T-") and ticket_id[2:].isdigit():
                numeric_ids.append(int(ticket_id[2:]))
        return f"T-{max(numeric_ids, default=1000) + 1:04d}"

    @staticmethod
    def _is_sla_breached(ticket):
        """Determine whether a stored ticket currently breaches its SLA.

        Args:
            ticket: Ticket data containing creation time, SLA, and status.

        Returns:
            bool: Whether the ticket has breached its SLA.
        """
        created_at = datetime.fromisoformat(ticket["created_at"])
        deadline = created_at + timedelta(hours=float(ticket["sla_hours"]))
        return deadline < datetime.now() and ticket["status"] != "closed"
