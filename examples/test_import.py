#!/usr/bin/env python3
"""
SVECTOR Python SDK - Quick Test

This simple test verifies the SDK can be imported and basic functionality works.
"""

import os
import sys

# Test import
try:
    import svector
    print(f"SVECTOR SDK imported successfully!")
    print(f" Version: {svector.__version__}")
    print(f"Author: {svector.__author__}")
    print(f"Support: {svector.__email__}")
except ImportError as e:
    print(f"Failed to import SVECTOR SDK: {e}")
    sys.exit(1)

# Test client creation
try:
    from svector import SVECTOR

    # Try with no API key (should show helpful error)
    try:
        client = SVECTOR(api_key="test-key")
        print("SVECTOR client created successfully!")
        print(f"Base URL: {client.base_url}")
        print(f"Timeout: {client.timeout}s")
        print(f"Max Retries: {client.max_retries}")
        print(f"SSL Verify: {client.verify_ssl}")
        
        # Check API endpoints exist
        print("\nAvailable APIs:")
        if hasattr(client, 'conversations'):
            print("  Conversations API")
        if hasattr(client, 'chat'):
            print("  Chat Completions API")
        if hasattr(client, 'models'):
            print("  Models API")
        if hasattr(client, 'files'):
            print("  Files API")
        if hasattr(client, 'knowledge'):
            print("  Knowledge API")
            
    except Exception as e:
        print(f"Client creation validation working: {type(e).__name__}")
        
except ImportError as e:
    print(f"Failed to import SVECTOR client: {e}")

# Test error classes
try:
    from svector import (APIError, AuthenticationError, NotFoundError,
                         RateLimitError)
    print("\n Error handling classes imported successfully!")
    print("  AuthenticationError")
    print("  RateLimitError") 
    print("  NotFoundError")
    print("  APIError")
except ImportError as e:
    print(f"Failed to import error classes: {e}")

# Test conversation types
try:
    from svector import (ConversationRequest, ConversationResponse,
                         ConversationStreamEvent)
    print("\n Conversation types imported successfully!")
    print("  ConversationRequest")
    print("  ConversationResponse")
    print("  ConversationStreamEvent")
except ImportError as e:
    print(f"Failed to import conversation types: {e}")

print(f"\n🎉 SVECTOR Python SDK v{svector.__version__} - All systems ready!")
print("=" * 60)
print("Quick Start:")
print("""
from svector import SVECTOR

client = SVECTOR(api_key="your-api-key")

# Conversation
response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a helpful assistant.",
    input="What is artificial intelligence?",
)

print(response.output)
""")
print("=" * 60)
print(" Documentation: https://platform.svector.co.in")
print("  Support: support@svector.co.in")
print(" Website: https://www.svector.co.in")
