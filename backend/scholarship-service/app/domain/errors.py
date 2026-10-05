class DomainError(Exception):
    """Base class for all domain errors."""


class InvalidScholarshipError(DomainError):
    """Raised when a Scholarship violates its invariants."""


class ScholarshipNotFoundError(DomainError):
    """Raised when a Scholarship does not exist."""
