"""
SVECTOR API Error Classes

Comprehensive error handling with specific error types for different scenarios.
"""


class SVECTORError(Exception):
    """Base exception for all SVECTOR API errors"""
    def __init__(self, message, status_code=None, request_id=None, headers=None):
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
        self.headers = headers or {}

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {super().__str__()}"
        return super().__str__()


class APIError(SVECTORError):
    """General API error"""
    pass


class AuthenticationError(SVECTORError):
    """Authentication failed - invalid API key or authentication issues"""
    pass


class PermissionDeniedError(SVECTORError):
    """Permission denied - insufficient permissions for the resource"""
    pass


class NotFoundError(SVECTORError):
    """Resource not found - requested resource does not exist"""
    pass


class RateLimitError(SVECTORError):
    """Rate limit exceeded - too many requests in a given time period"""
    pass


class UnprocessableEntityError(SVECTORError):
    """Unprocessable entity - invalid request data or parameters"""
    pass


class InternalServerError(SVECTORError):
    """Internal server error - server-side issues"""
    pass


class APIConnectionError(SVECTORError):
    """Network connection issues - failed to connect to API"""
    pass


class APIConnectionTimeoutError(SVECTORError):
    """Request timeout - request took too long to complete"""
    pass


class ValidationError(SVECTORError):
    """Validation error - invalid input parameters"""
    pass


class ServerError(SVECTORError):
    """Server-side error"""
    pass


class ConnectionError(SVECTORError):
    """Connection error"""
    pass


class TimeoutError(SVECTORError):
    """Timeout error"""
    pass
