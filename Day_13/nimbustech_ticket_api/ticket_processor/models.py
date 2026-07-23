"""Data models used by the ticket processing script."""

from dataclasses import asdict, dataclass
from datetime import datetime


@dataclass
class Ticket:
    """Represent one validated and classified support ticket.

    Args:
        ticket_id: Unique ticket identifier.
        customer_name: Name of the customer that opened the ticket.
        category: Ticket category.
        priority_raw: Normalized priority text from the export.
        priority_score: Numeric score assigned to the priority.
        created_at: Date and time the ticket was created.
        sla_hours: Positive SLA period in hours.
        status: Current ticket status.
        sla_breached: Whether the ticket has exceeded its SLA.
    """

    ticket_id: str
    customer_name: str
    category: str
    priority_raw: str
    priority_score: int
    created_at: datetime
    sla_hours: float
    status: str
    sla_breached: bool

    def to_dict(self):
        """Return the ticket in a JSON-serializable format.

        Returns:
            dict: Ticket fields, with the creation date in ISO 8601 format.
        """
        ticket_data = asdict(self)
        ticket_data["created_at"] = self.created_at.isoformat()
        return ticket_data
