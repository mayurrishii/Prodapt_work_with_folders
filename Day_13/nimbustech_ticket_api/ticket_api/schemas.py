"""
Pydantic schemas ("shapes" of data going in/out over the API).

Single responsibility of this file: define what valid JSON looks like
for returning tickets. This is where response serialization happens.

Keeping this separate from models.py (Pydantic request models) and
db_models.py (SQLAlchemy ORM models) is a deliberate layering choice:
- models.py describes the API's INPUT JSON validation.
- db_models.py describes the DATABASE table.
- schemas.py describes the API's OUTPUT JSON shape.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TicketOut(BaseModel):
    """
    Response shape returned to clients - includes all ticket fields.
    """

    id: int
    ticket_id: str
    customer_name: str
    category: str
    priority_raw: str
    priority_score: int
    created_at: datetime
    sla_hours: float
    status: str
    sla_breached: bool

    class Config:
        # Lets Pydantic build this schema directly from a SQLAlchemy
        # model instance instead of requiring a plain dict.
        from_attributes = True


class TicketSummary(BaseModel):
    """Response shape for the summary endpoint."""

    total_tickets: int
    breached_count: int
    by_category: dict