#!/usr/bin/env python3
"""
Simple test for SVECTOR Vision API

This is a basic test to verify the vision functionality works correctly.
"""

import os
import sys
from pathlib import Path

# Add the svector package to the path
sys.path.insert(0, str(Path(__file__).parent / "svector"))

from svector import SVECTOR


def test_vision_basic():
    """Test basic vision functionality"""
    
    # Check for API key
    api_key = os.getenv("SVECTOR_API_KEY")
    if not api_key:
        print("❌ Please set SVECTOR_API_KEY environment variable")
        return False
    
    try:
        # Initialize client
        client = SVECTOR(api_key=api_key)
        
        # Test 1: Basic vision analysis
        print("🔍 Testing basic vision analysis...")
        response = client.vision.analyze_from_url(
            image_url="https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg",
            prompt="What do you see in this image?",
            model="spec-3-turbo",
            max_tokens=200
        )
        print(f"✅ Basic analysis successful: {response.analysis[:100]}...")
        
        # Test 2: Responses API format
        print("\n📋 Testing responses API format...")
        response = client.responses.create(
            model="spec-3-turbo",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "what's in this image?"},
                    {
                        "type": "input_image",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg",
                    },
                ],
            }],
        )
        print(f"✅ Responses API successful: {response.output_text[:100]}...")
        
        # Test 3: OCR
        print("\n📝 Testing OCR functionality...")
        response = client.vision.extract_text(
            image_url="https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg",
            model="spec-3-turbo"
        )
        print(f"✅ OCR successful: {response.analysis[:100]}...")
        
        print("\n🎉 All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_vision_basic()
    sys.exit(0 if success else 1)
