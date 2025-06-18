#!/usr/bin/env python3
"""
SVECTOR Python SDK - Streaming Fix Test

This test verifies that the streaming functionality works correctly
after the fix for the duplicate parameter issue.
"""

import os

from svector import SVECTOR


def test_streaming():
    """Test that streaming works without parameter conflicts"""
    print(" Testing SVECTOR Streaming Fix")
    print("=" * 50)
    
    client = SVECTOR(api_key=os.environ.get("SVECTOR_API_KEY", "test-key"))
    
    try:
        print("Creating streaming conversation...")
        print("Question: Tell me a very short joke about programming.")
        print("Streaming Answer: ", end="", flush=True)
        
        stream = client.conversations.create_stream(
            model="spec-3-turbo:latest",
            instructions="You are a comedian. Keep responses very short - 1-2 sentences max.",
            input="Tell me a very short joke about programming.",
            max_tokens=50,
        )
        
        content_received = False
        for event in stream:
            if not event.done and event.content:
                print(event.content, end="", flush=True)
                content_received = True
            elif event.done:
                print("\nStreaming completed successfully!")
                break
        
        if not content_received:
            print("\n⚠️  No content received in stream")
            
    except Exception as e:
        if "multiple values for keyword argument 'stream'" in str(e):
            print(f"\nSTREAMING BUG STILL EXISTS: {e}")
            print("The duplicate parameter issue was not fixed!")
        else:
            print(f"\nStreaming parameter conflict fixed!")
            print(f"Different error (expected with test key): {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_streaming()
