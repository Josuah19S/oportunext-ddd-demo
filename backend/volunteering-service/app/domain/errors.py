class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidVolunteeringError(DomainError):
    """Raised when a Volunteering violates its invariants."""


class VolunteeringNotFoundError(DomainError):
    """Raised when a Volunteering does not exist."""
