"""Data models used by the ticket processing script."""

from datetime import datetime


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

    def __init__(
        self,
        ticket_id,
        customer_name,
        category,
        priority_raw,
        priority_score,
        created_at,
        sla_hours,
        status,
        sla_breached,
    ):
        """Initialize a validated and classified support ticket.

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
        self.ticket_id = ticket_id
        self.customer_name = customer_name
        self.category = category
        self.priority_raw = priority_raw
        self.priority_score = priority_score
        self.created_at = created_at
        self.sla_hours = sla_hours
        self.status = status
        self.sla_breached = sla_breached

    def to_dict(self):
        """Return the ticket in a JSON-serializable format.

        Returns:
            dict: Ticket fields, with the creation date in ISO 8601 format.
        """
        return {
            "ticket_id": self.ticket_id,
            "customer_name": self.customer_name,
            "category": self.category,
            "priority_raw": self.priority_raw,
            "priority_score": self.priority_score,
            "created_at": self.created_at.isoformat(),
            "sla_hours": self.sla_hours,
            "status": self.status,
            "sla_breached": self.sla_breached,
        }
