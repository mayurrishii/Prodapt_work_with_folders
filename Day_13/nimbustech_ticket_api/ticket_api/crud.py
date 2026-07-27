"""
CRUD layer: the only place that talks directly to the database session.

Single responsibility of this file: take a SQLAlchemy `Session` plus
some plain Python arguments, and do the actual `db.add` / `db.query` /
`db.delete` / `db.commit` work.

WHY keep this separate from main.py?
  1. Single Responsibility: main.py's job is to handle HTTP concerns
     (status codes, path/query params). It shouldn't also contain
     database query logic - that's a different concern, and mixing
     them makes both harder to read.
  2. Testability: these functions take a plain `Session` and return
     plain Python/SQLAlchemy objects - no `Request`/`Response` objects
     involved. That means we can unit-test `create_ticket`, `get_ticket`,
     etc. directly, without spinning up a whole FastAPI app.
  3. Reuse: if we ever added a CLI tool or a background job that also
     needs to create/update tickets, it could import these same
     functions instead of duplicating query logic.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from .config import PRIORITY_SCORES
from .db_models import Ticket
from .exceptions import TicketNotFoundException
from .models import TicketCreate, TicketUpdate

logger = logging.getLogger("ticket_api.crud")


def _compute_sla_breached(ticket: Ticket) -> bool:
    """Determine whether a ticket currently breaches its SLA."""
    if ticket.status == "closed":
        return False
    deadline = ticket.created_at + timedelta(hours=ticket.sla_hours)
    return deadline < datetime.now(tz=ticket.created_at.tzinfo)


def _next_ticket_id(db: Session) -> str:
    """Generate the next sequential NimbusTech ticket ID (e.g. T-1001)."""
    last_ticket = (
        db.query(Ticket)
        .filter(Ticket.ticket_id.like("T-%"))
        .order_by(Ticket.id.desc())
        .first()
    )
    if last_ticket is None:
        return "T-1001"
    numeric_part = last_ticket.ticket_id.split("-")[1]
    try:
        next_num = int(numeric_part) + 1
    except ValueError:
        next_num = 1001
    return f"T-{next_num:04d}"


def create_ticket(db: Session, ticket_in: TicketCreate) -> Ticket:
    """Insert a new ticket row and return it (with id/ticket_id/created_at filled in)."""
    ticket = Ticket(
        ticket_id=_next_ticket_id(db),
        customer_name=ticket_in.customer_name,
        category=ticket_in.category.lower(),
        priority_raw=ticket_in.priority_raw,
        priority_score=PRIORITY_SCORES[ticket_in.priority_raw],
        sla_hours=ticket_in.sla_hours,
        status=ticket_in.status,
        sla_breached=False,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    # Recompute sla_breached now that we have created_at from the DB
    ticket.sla_breached = _compute_sla_breached(ticket)
    db.commit()
    db.refresh(ticket)
    logger.info("Created ticket %s id=%s", ticket.ticket_id, ticket.id)
    return ticket


def get_ticket(db: Session, ticket_id: str) -> Ticket:
    """
    Fetch a single ticket by its public ticket_id, or raise
    TicketNotFoundException if it doesn't exist.
    """
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    if ticket is None:
        raise TicketNotFoundException(ticket_id)
    return ticket


def get_tickets(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    breached: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
):
    """
    Return a filtered, paginated list of tickets.

    Building the query step-by-step (start broad, then narrow it down
    with `.filter(...)` calls) is a common SQLAlchemy pattern - nothing
    actually hits the database until we call `.all()` at the end.
    """
    query = db.query(Ticket)

    if status:
        query = query.filter(Ticket.status == status)

    if priority:
        query = query.filter(Ticket.priority_raw == priority)

    if category:
        query = query.filter(Ticket.category == category)

    if breached is not None:
        query = query.filter(Ticket.sla_breached == breached)

    query = query.order_by(Ticket.created_at.desc())

    return query.offset(offset).limit(limit).all()


def update_ticket(db: Session, ticket_id: str, ticket_in: TicketUpdate) -> Ticket:
    """
    Apply a partial update to an existing ticket: only fields the client
    actually sent (`exclude_none=True`) are changed.
    """
    ticket = get_ticket(db, ticket_id)  # raises TicketNotFoundException if missing

    updates = ticket_in.model_dump(exclude_none=True)
    for field, value in updates.items():
        setattr(ticket, field, value)

    # If priority changed, recalculate the score
    if "priority_raw" in updates:
        ticket.priority_score = PRIORITY_SCORES[ticket.priority_raw]

    # Recompute SLA breach status
    ticket.sla_breached = _compute_sla_breached(ticket)

    db.commit()
    db.refresh(ticket)
    logger.info("Updated ticket %s fields=%s", ticket.ticket_id, list(updates.keys()))
    return ticket


def delete_ticket(db: Session, ticket_id: str) -> None:
    """Delete a ticket by its ticket_id, raising TicketNotFoundException if missing."""
    ticket = get_ticket(db, ticket_id)  # raises TicketNotFoundException if missing
    db.delete(ticket)
    db.commit()
    logger.info("Deleted ticket %s", ticket_id)


def get_summary(db: Session) -> dict:
    """
    Build the aggregate counts for tickets.
    """
    total = db.query(Ticket).count()
    breached_count = db.query(Ticket).filter(Ticket.sla_breached == True).count()  # noqa: E712

    # Count by category
    from sqlalchemy import func as sqlfunc

    category_rows = (
        db.query(Ticket.category, sqlfunc.count(Ticket.id))
        .group_by(Ticket.category)
        .all()
    )
    by_category = {row[0]: row[1] for row in category_rows}

    return {
        "total_tickets": total,
        "breached_count": breached_count,
        "by_category": by_category,
    }