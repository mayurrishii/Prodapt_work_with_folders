"""
Custom application exceptions for the NimbusTech Ticket API.

Single responsibility of this file: define our own exception types so
that the CRUD/router layers can raise a clear, meaningful error
(e.g. "TicketNotFoundException") instead of scattering raw
`HTTPException(status_code=404, ...)` calls everywhere. main.py then
registers a single `@app.exception_handler` that knows how to turn
this exception into a clean JSON response.

This is a common industry pattern: keep domain-level errors separate
from the HTTP-response details.
"""


class TicketNotFoundException(Exception):
    """Raised whenever code looks up a ticket by ticket_id and doesn't find one."""

    def __init__(self, ticket_id: str):
        self.ticket_id = ticket_id
        super().__init__(f"Ticket with id {ticket_id} not found")