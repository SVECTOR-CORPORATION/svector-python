"""
SVE__version__ = "1.0.5"TOR Python SDK

Official Python client for SVECTOR AI Models.
Advanced conversational AI and language models.
"""

__version__ = "1.0.4"
__author__ = "SVECTOR Team"
__email__ = "support@svector.co.in"

from .client import SVECTOR
from .errors import (APIError, AuthenticationError, NotFoundError,
                     PermissionDeniedError, RateLimitError, SVectorError,
                     UnprocessableEntityError)

__all__ = [
    "SVECTOR",
    "SVectorError",
    "APIError", 
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "PermissionDeniedError",
    "UnprocessableEntityError"
]
