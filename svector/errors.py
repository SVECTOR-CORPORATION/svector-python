"""
SVECTOR API Error Classes

Comprehensive error handling with specific error types for different scenarios.
"""


class SVectorError(Exception):
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


class APIError(SVectorError):
    """General API error"""
    pass


class AuthenticationError(SVectorError):
    """Authentication failed - invalid API key or authentication issues"""
    pass


class PermissionDeniedError(SVectorError):
    """Permission denied - insufficient permissions for the resource"""
    pass


class NotFoundError(SVectorError):
    """Resource not found - requested resource does not exist"""
    pass


class RateLimitError(SVectorError):
    """Rate limit exceeded - too many requests in a given time period"""
    pass


class UnprocessableEntityError(SVectorError):
    """Unprocessable entity - invalid request data or parameters"""
    pass


class InternalServerError(SVectorError):
    """Internal server error - server-side issues"""
    pass


class APIConnectionError(SVectorError):
    """Network connection issues - failed to connect to API"""
    pass


class APIConnectionTimeoutError(SVectorError):
    """Request timeout - request took too long to complete"""
    pass


class ValidationError(SVectorError):
    """Validation error - invalid input parameters"""
    pass


class ServerError(SVectorError):
    """Server-side error"""
    pass


class ConnectionError(SVectorError):
    """Connection error"""
    pass


class TimeoutError(SVectorError):
    """Timeout error"""
    pass
