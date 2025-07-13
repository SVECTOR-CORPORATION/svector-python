"""
SVECTOR Python SDK

Official Python client for SVECTOR AI Models.
Advanced conversational AI and language models with API.
"""

__version__ = "1.3.1"
__author__ = "SVECTOR Team"
__email__ = "support@svector.co.in"
__author__ = "SVECTOR Team"
__email__ = "support@svector.co.in"

from .client import SVECTOR, AsyncSVECTOR
from .conversations import (AsyncConversationsAPI, ConversationRequest,
                            ConversationResponse, ConversationsAPI,
                            ConversationStreamEvent)
from .errors import (APIConnectionError, APIConnectionTimeoutError, APIError,
                     AuthenticationError, ConnectionError, InternalServerError,
                     NotFoundError, PermissionDeniedError, RateLimitError,
                     ServerError, SVectorError, TimeoutError,
                     UnprocessableEntityError, ValidationError)

__all__ = [
    # Main clients
    "SVECTOR",
    "AsyncSVECTOR",
    
    # Conversations API
    "ConversationRequest",
    "ConversationResponse", 
    "ConversationStreamEvent",
    "ConversationsAPI",
    "AsyncConversationsAPI",
    
    # Error classes
    "SVectorError",
    "APIError", 
    "AuthenticationError",
    "RateLimitError",
    "NotFoundError",
    "PermissionDeniedError",
    "UnprocessableEntityError",
    "InternalServerError",
    "APIConnectionError",
    "APIConnectionTimeoutError",
    "ValidationError",
    "ServerError",
    "ConnectionError",
    "TimeoutError"
]
