"""FastAPI application for the NimbusTech ticket dashboard."""

import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .models import TicketCreate, TicketUpdate
from .store import TicketStore

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

app = FastAPI(title="NimbusTech Ticket Triage API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
store = TicketStore()


@app.on_event("startup")
def load_ticket_report():
    """Load the Module 1 report when the API starts.

    Returns:
        None
    """
    store.load_report()


@app.get("/")
def read_root():
    """Return the API health and service name.

    Returns:
        dict: Basic API status payload.
    """
    return {"status": "ok", "service": "nimbustech-ticket-triage-api"}


@app.get("/tickets")
def list_tickets():
    """Return all in-memory tickets.

    Returns:
        list[dict]: All tickets currently loaded by the API.
    """
    return store.tickets


@app.get("/tickets/breached")
def list_breached_tickets():
    """Return only tickets that have breached their SLA.

    Returns:
        list[dict]: Current SLA-breached tickets.
    """
    return [ticket for ticket in store.tickets if ticket["sla_breached"]]


@app.get("/tickets/summary")
def get_ticket_summary():
    """Return summary counts for the current in-memory ticket list.

    Returns:
        dict: Ticket summary counts and category breakdown.
    """
    return store.get_summary()


@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id):
    """Return a ticket by its identifier.

    Args:
        ticket_id: Identifier of the requested ticket.

    Returns:
        dict: Requested ticket.

    Raises:
        HTTPException: If no ticket has the requested identifier.
    """
    ticket = store.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.post("/tickets", status_code=status.HTTP_201_CREATED)
def create_ticket(ticket_data: TicketCreate):
    """Create a new in-memory ticket.

    Args:
        ticket_data: Validated JSON request body.

    Returns:
        dict: Newly created ticket.
    """
    return store.create_ticket(ticket_data)


@app.put("/tickets/{ticket_id}")
def update_ticket(ticket_id, ticket_data: TicketUpdate):
    """Update the status and/or priority of a ticket.

    Args:
        ticket_id: Identifier of the ticket to update.
        ticket_data: Validated JSON update body.

    Returns:
        dict: Updated ticket.

    Raises:
        HTTPException: If no ticket has the requested identifier.
    """
    ticket = store.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return store.update_ticket(ticket, ticket_data)


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id):
    """Delete an in-memory ticket.

    Args:
        ticket_id: Identifier of the ticket to delete.

    Returns:
        dict: Confirmation of the deleted ticket identifier.

    Raises:
        HTTPException: If no ticket has the requested identifier.
    """
    ticket = store.get_ticket(ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    store.delete_ticket(ticket)
    return {"message": "Ticket deleted", "ticket_id": ticket_id}
