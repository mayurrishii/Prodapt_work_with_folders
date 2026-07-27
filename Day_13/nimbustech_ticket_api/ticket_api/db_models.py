"""
SQLAlchemy ORM models for the NimbusTech Ticket API.

Single responsibility of this file: describe what a "Ticket" looks like
as a database TABLE (columns, types, defaults). This is the "M" in a
typical layered architecture - it knows nothing about HTTP, JSON, or
FastAPI. Validation of INCOMING data is deliberately handled in Pydantic
schemas (models.py), not here, to keep the database layer simple.
"""

from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func

from .database import Base


class Ticket(Base):
    """The `tickets` table: a single support ticket."""

    __tablename__ = "tickets"

    # Auto-incrementing primary key (internal DB id).
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)

    # Public-facing ticket identifier, e.g. "T-1001".
    ticket_id = Column(String(20), unique=True, nullable=False, index=True)

    # Customer who submitted the ticket.
    customer_name = Column(String(200), nullable=False)

    # Category of the issue (e.g. "billing", "technical").
    category = Column(String(100), nullable=False)

    # Priority: "low", "medium", "high", "critical".
    priority_raw = Column(String(20), nullable=False)

    # Numeric score derived from priority_raw (1-4).
    priority_score = Column(Integer, nullable=False)

    # When the ticket was created (ISO format string stored in DB).
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Number of hours within which the ticket should be resolved.
    sla_hours = Column(Float, nullable=False)

    # Current status: "open", "in_progress", "resolved", "closed".
    status = Column(String(20), nullable=False, default="open")

    # Whether the ticket has breached its SLA deadline.
    sla_breached = Column(Boolean, nullable=False, default=False)