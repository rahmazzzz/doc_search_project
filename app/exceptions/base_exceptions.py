class AppException(Exception):
    """
    Base class for all custom exceptions in the application.
    Designed to work well with FastAPI or any HTTP-based service.
    """
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


class ServiceError(AppException):
    """Raised for internal service-related errors (logic, processing)."""
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(detail=detail, status_code=status_code)


class ExternalServiceError(AppException):
    """Raised when an external dependency or API fails."""
    def __init__(self, detail: str, status_code: int = 502):
        super().__init__(detail=detail, status_code=status_code)
