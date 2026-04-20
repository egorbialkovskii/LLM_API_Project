class AppError(Exception):
    """Base application error for domain and service layers."""

    def __init__(self, message: str = "Application error") -> None:
        self.message = message
        super().__init__(message)


class ConflictError(AppError):
    """Raised when an entity conflicts with existing data."""
    pass


class UnauthorizedError(AppError):
    """Raised when authentication fails."""
    pass


class NotFoundError(AppError):
    """Raised when an entity cannot be found."""
    pass


class ExternalServiceError(AppError):
    """Raised when an external service returns an error."""
    pass
