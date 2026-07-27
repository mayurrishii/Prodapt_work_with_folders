"""
Application entry point for the NimbusTech Ticket API.

Single responsibility of this file: wire everything else together -
create the FastAPI app, configure logging/CORS, create the database
tables, register our custom error handlers, and define the routes.
Run it with:

    uvicorn ticket_api.main:app --reload

then open http://127.0.0.1:8000/docs
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import db_models
from .config import CORS_ORIGINS
from .database import engine, get_db
from .exceptions import TicketNotFoundException
from . import crud
from .models import TicketCreate, TicketUpdate
from .schemas import TicketOut, TicketSummary

# --- Logging -----------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ticket_api.main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI "lifespan" function: code before `yield` runs once at
    startup, code after `yield` runs once at shutdown. We use it to
    create the database tables (if they don't exist yet).
    """
    db_models.Base.metadata.create_all(bind=engine)
    logger.info("NimbusTech Ticket API is starting up.")
    yield
    logger.info("NimbusTech Ticket API is shutting down.")


app = FastAPI(
    title="NimbusTech Ticket Triage API",
    description="A FastAPI + SQLAlchemy + SQLite ticket management API.",
    version="2.0.0",
    lifespan=lifespan,
)

# --- CORS ----------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Custom exception handlers -------------------------------------------
@app.exception_handler(TicketNotFoundException)
async def ticket_not_found_handler(request: Request, exc: TicketNotFoundException):
    """
    Turns our domain-level TicketNotFoundException (raised in crud.py)
    into a clean 404 JSON response.
    """
    return JSONResponse(
        status_code=404,
        content={"detail": f"Ticket with id {exc.ticket_id} not found"},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Catch-all safety net: if ANYTHING unexpected goes wrong, we log the
    real error server-side and return a generic 500 response to the client.
    """
    logger.exception(
        "Unhandled error while processing request: %s %s",
        request.method,
        request.url,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# --- Routes ---------------------------------------------------------------

@app.get("/")
def read_root():
    """Return the API health and service name."""
    return {"status": "ok", "service": "nimbustech-ticket-triage-api"}


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets(
    status_filter: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    breached: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    """
    Return all tickets, with optional filtering by status, priority,
    category, or SLA breach status.
    """
    return crud.get_tickets(
        db,
        status=status_filter,
        priority=priority,
        category=category,
        breached=breached,
        limit=limit,
        offset=offset,
    )


@app.get("/tickets/breached", response_model=list[TicketOut])
def list_breached_tickets(db: Session = Depends(get_db)):
    """Return only tickets that have breached their SLA."""
    return crud.get_tickets(db, breached=True)


@app.get("/tickets/summary", response_model=TicketSummary)
def get_ticket_summary(db: Session = Depends(get_db)):
    """Return summary counts for tickets."""
    return crud.get_summary(db)


@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """
    Return a ticket by its identifier (e.g. T-1001).

    If it doesn't exist, `crud.get_ticket` raises TicketNotFoundException,
    which main.py's exception handler turns into a clean 404 JSON response.
    """
    return crud.get_ticket(db, ticket_id)


@app.post("/tickets", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_data: TicketCreate, db: Session = Depends(get_db)):
    """Create a new ticket."""
    return crud.create_ticket(db, ticket_data)


@app.put("/tickets/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: str,
    ticket_data: TicketUpdate,
    db: Session = Depends(get_db),
):
    """Update the status and/or priority of a ticket."""
    return crud.update_ticket(db, ticket_id, ticket_data)


@app.delete("/tickets/{ticket_id}", status_code=204)
def delete_ticket(ticket_id: str, db: Session = Depends(get_db)):
    """Delete a ticket. Returns 204 No Content on success."""
    crud.delete_ticket(db, ticket_id)
    return Response(status_code=204)