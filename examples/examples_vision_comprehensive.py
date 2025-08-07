#!/usr/bin/env python3
"""
Comprehensive SVECTOR Vision API Examples for Python

This file demonstrates all the vision capabilities available in the SVECTOR Python SDK,
matching the functionality available in the Node.js/JSR SDK.

Features demonstrated:
- Basic image analysis from URLs, base64, and file IDs
- Advanced vision features (OCR, accessibility, object detection)
- Batch processing
- Confidence scoring
- Caption generation
- Image comparison
- Error handling and best practices

Requirements:
    pip install svector-sdk

Setup:
    export SVECTOR_API_KEY="your-api-key-here"
"""

import base64
import os
import time
from pathlib import Path
from typing import Any, Dict, List

from svector import SVECTOR, create_data_url, encode_image


def main():
    """Run all vision examples"""
    # Initialize client
    client = SVECTOR(
        api_key=os.getenv("SVECTOR_API_KEY"),
        timeout=60  # Increased timeout for vision requests
    )
    
    print("🚀 SVECTOR Python Vision API Examples")
    print("=" * 50)
    
    # Run examples
    basic_examples(client)
    advanced_examples(client)
    utility_examples(client)
    batch_examples(client)
    error_handling_examples(client)
    
    print("\n✅ All examples completed!")


def basic_examples(client: SVECTOR):
    """Basic vision analysis examples"""
    print("\n📸 BASIC VISION EXAMPLES")
    print("-" * 30)
    
    # Example 1: Analyze image from URL
    print("\n1. 🔗 Analyzing image from URL...")
    try:
        response = client.vision.analyze_from_url(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            prompt="What do you see in this image? Describe the scene in detail.",
            model="spec-3-turbo",
            max_tokens=500,
            detail="high"
        )
        print(f"Analysis: {response.analysis[:200]}...")
        print(f"Usage: {response.usage}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Responses API format (matching Node.js examples)
    print("\n2. 📋 Using responses.create format...")
    try:
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
        print(f"Output: {response.output_text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Base64 image analysis
    print("\n3. 📁 Analyzing image from base64...")
    try:
        # Create a simple test image or use a placeholder
        sample_image_url = "https://via.placeholder.com/300x200.png?text=Sample+Image"
        
        # For demo, we'll use the responses format with base64
        response = client.responses.create(
            model="spec-3-turbo",
            input=[
                {
                    "role": "user",
                    "content": [
                        { "type": "input_text", "text": "what's in this image?" },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg==",
                        },
                    ],
                }
            ],
        )
        print(f"Output: {response.output_text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: File upload and analysis
    print("\n4. 📤 File upload and analysis...")
    try:
        # Note: For this example to work, you'd need to upload a real file
        # This is a placeholder showing the pattern
        print("This would upload a file and analyze it by file_id")
        print("Pattern: client.files.create() -> client.vision.analyze_from_file_id()")
    except Exception as e:
        print(f"Error: {e}")


def advanced_examples(client: SVECTOR):
    """Advanced vision features"""
    print("\n🔧 ADVANCED VISION FEATURES")
    print("-" * 30)
    
    # Example 1: OCR - Extract text from image
    print("\n1. 📝 OCR - Extract text from image...")
    try:
        response = client.vision.extract_text(
            image_url="https://via.placeholder.com/400x200.png?text=Hello+World+OCR+Test",
            model="spec-3-turbo",
            max_tokens=500
        )
        print(f"Extracted text: {response.analysis}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Accessibility descriptions
    print("\n2. ♿ Accessibility description...")
    try:
        response = client.vision.describe_for_accessibility(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            model="spec-3-turbo"
        )
        print(f"Accessibility description: {response.analysis[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Object detection
    print("\n3. 🎯 Object detection...")
    try:
        response = client.vision.detect_objects(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            object_types=['trees', 'boardwalk', 'sky', 'grass', 'mountains'],
            model="spec-3-turbo"
        )
        print(f"Detected objects: {response.analysis[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Image comparison
    print("\n4. 🔍 Image comparison...")
    try:
        images = [
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"},
            {"url": "https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg"}
        ]
        
        response = client.vision.compare_images(
            images=images,
            prompt="Compare these two images and describe their differences.",
            model="spec-3-turbo"
        )
        print(f"Comparison: {response.analysis[:200]}...")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Caption generation
    print("\n5. 📝 Caption generation...")
    try:
        styles = ["casual", "professional", "funny", "technical"]
        
        for style in styles[:2]:  # Test first 2 styles
            response = client.vision.generate_caption(
                image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                style=style,
                model="spec-3-turbo"
            )
            print(f"{style.title()} caption: {response.analysis[:100]}...")
    except Exception as e:
        print(f"Error: {e}")


def utility_examples(client: SVECTOR):
    """Utility functions and advanced features"""
    print("\n🛠️ UTILITY EXAMPLES")
    print("-" * 30)
    
    # Example 1: Confidence scoring
    print("\n1. 🎯 Confidence scoring...")
    try:
        result = client.vision.analyze_with_confidence(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            prompt="Analyze this nature scene",
            model="spec-3-turbo"
        )
        print(f"Analysis: {result['analysis'][:100]}...")
        print(f"Confidence: {result['confidence']}%")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Using create_response (advanced format)
    print("\n2. 🔧 Advanced create_response format...")
    try:
        response = client.vision.create_response(
            model="spec-3-turbo",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "Provide a technical analysis of this image"},
                    {"type": "input_image", "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg"}
                ]
            }],
            max_tokens=500,
            temperature=0.7
        )
        print(f"Technical analysis: {response.analysis[:150]}...")
    except Exception as e:
        print(f"Error: {e}")


def batch_examples(client: SVECTOR):
    """Batch processing examples"""
    print("\n📦 BATCH PROCESSING")
    print("-" * 30)
    
    # Example 1: Batch analyze multiple images
    print("\n1. 🔄 Batch image analysis...")
    try:
        images = [
            {
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                "prompt": "Describe this nature scene"
            },
            {
                "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg",
                "prompt": "What is this logo?"
            }
        ]
        
        results = client.vision.batch_analyze(
            images=images,
            model="spec-3-turbo",
            delay=1.0  # 1 second delay between requests
        )
        
        for i, result in enumerate(results):
            if "error" in result:
                print(f"Image {i+1} error: {result['error']}")
            else:
                print(f"Image {i+1}: {result['analysis'][:100]}...")
                
    except Exception as e:
        print(f"Error: {e}")


def error_handling_examples(client: SVECTOR):
    """Error handling and best practices"""
    print("\n⚠️ ERROR HANDLING")
    print("-" * 30)
    
    # Example 1: Handling timeout errors
    print("\n1. ⏰ Timeout handling...")
    try:
        response = client.vision.analyze_from_url(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            prompt="Analyze this image",
            timeout=5,  # Very short timeout for demo
            max_retries=1
        )
        print("Analysis successful")
    except Exception as e:
        print(f"Expected timeout or error: {type(e).__name__}: {e}")
    
    # Example 2: Invalid image URL
    print("\n2. 🚫 Invalid image URL...")
    try:
        response = client.vision.analyze_from_url(
            image_url="https://invalid-url-that-does-not-exist.com/image.jpg",
            prompt="Analyze this image"
        )
        print("Analysis successful")
    except Exception as e:
        print(f"Expected error: {type(e).__name__}: {e}")
    
    # Example 3: Best practices example
    print("\n3. ✅ Best practices example...")
    try:
        response = client.vision.analyze_from_url(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            prompt="Provide a comprehensive analysis of this image including colors, objects, and mood.",
            model="spec-3-turbo",
            max_tokens=800,
            temperature=0.7,
            detail="high",
            timeout=60,
            max_retries=2
        )
        print(f"Best practices analysis: {response.analysis[:150]}...")
        print(f"Request ID: {response.request_id}")
        print(f"Token usage: {response.usage}")
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")


def demonstrate_utility_functions():
    """Demonstrate utility functions"""
    print("\n🔧 UTILITY FUNCTIONS")
    print("-" * 30)
    
    # Example 1: encode_image function
    print("\n1. 📷 encode_image function...")
    try:
        # This would work with a real image file
        print("Example usage:")
        print('base64_image = encode_image("path/to/your/image.jpg")')
        print("# Returns base64 encoded string")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: create_data_url function
    print("\n2. 🔗 create_data_url function...")
    try:
        sample_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        data_url = create_data_url(sample_base64, "image/png")
        print(f"Data URL: {data_url[:80]}...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("SVECTOR_API_KEY"):
        print("❌ Please set SVECTOR_API_KEY environment variable")
        print("   export SVECTOR_API_KEY='your-api-key-here'")
        exit(1)
    
    main()
    demonstrate_utility_functions()
