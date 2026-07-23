"""Pydantic request models for the ticket API."""

from pydantic import BaseModel, Field, field_validator, model_validator

from .config import PRIORITY_SCORES, VALID_STATUSES


class TicketCreate(BaseModel):
    """Validate the JSON body used to create a ticket."""

    customer_name: str = Field(min_length=1)
    category: str = Field(min_length=1)
    priority_raw: str
    sla_hours: float = Field(gt=0)
    status: str

    @field_validator("customer_name", "category")
    @classmethod
    def strip_required_text(cls, value):
        """Reject required text fields containing only whitespace.

        Args:
            value: Submitted text value.

        Returns:
            str: Trimmed text value.
        """
        value = value.strip()
        if not value:
            raise ValueError("value must not be empty")
        return value

    @field_validator("priority_raw")
    @classmethod
    def validate_priority(cls, value):
        """Normalize and validate a submitted priority.

        Args:
            value: Submitted priority text.

        Returns:
            str: Valid normalized priority.
        """
        priority = value.strip().lower()
        if priority not in PRIORITY_SCORES:
            raise ValueError("priority_raw must be low, medium, high, or critical")
        return priority

    @field_validator("status")
    @classmethod
    def validate_status(cls, value):
        """Normalize and validate a submitted ticket status.

        Args:
            value: Submitted status text.

        Returns:
            str: Valid normalized status.
        """
        status = value.strip().lower()
        if status not in VALID_STATUSES:
            raise ValueError("status must be open, in_progress, resolved, or closed")
        return status


class TicketUpdate(BaseModel):
    """Validate the JSON body used to update a ticket."""

    status: str | None = None
    priority_raw: str | None = None

    @field_validator("priority_raw")
    @classmethod
    def validate_optional_priority(cls, value):
        """Normalize an optional submitted priority.

        Args:
            value: Optional submitted priority text.

        Returns:
            str | None: Valid normalized priority, when provided.
        """
        if value is None:
            return value
        priority = value.strip().lower()
        if priority not in PRIORITY_SCORES:
            raise ValueError("priority_raw must be low, medium, high, or critical")
        return priority

    @field_validator("status")
    @classmethod
    def validate_optional_status(cls, value):
        """Normalize an optional submitted ticket status.

        Args:
            value: Optional submitted status text.

        Returns:
            str | None: Valid normalized status, when provided.
        """
        if value is None:
            return value
        status = value.strip().lower()
        if status not in VALID_STATUSES:
            raise ValueError("status must be open, in_progress, resolved, or closed")
        return status

    @model_validator(mode="after")
    def require_update(self):
        """Require at least one updateable field.

        Returns:
            TicketUpdate: Validated update request.
        """
        if self.status is None and self.priority_raw is None:
            raise ValueError("provide status and/or priority_raw")
        return self
