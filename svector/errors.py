"""
SVECTOR API Error Classes
"""

class SVectorError(Exception):
    """Base exception for all SVECTOR API errors"""
    def __init__(self, message, status_code=None, request_id=None, headers=None):
        super().__init__(message)
        self.status_code = status_code
        self.request_id = request_id
        self.headers = headers or {}

class APIError(SVectorError):
    """General API error"""
    pass

class AuthenticationError(SVectorError):
    """Authentication failed - invalid API key"""
    pass

class RateLimitError(SVectorError):
    """Rate limit exceeded"""
    pass

class NotFoundError(SVectorError):
    """Resource not found"""
    pass

class PermissionDeniedError(SVectorError):
    """Permission denied"""
    pass

class UnprocessableEntityError(SVectorError):
    """Unprocessable entity - validation error"""
    pass
