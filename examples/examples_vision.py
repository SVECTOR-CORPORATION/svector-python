#!/usr/bin/env python3
"""
SVECTOR Python SDK - Vision API Examples

This file demonstrates various vision capabilities of the SVECTOR Python SDK.
"""

import base64
import os
from pathlib import Path

# Import SVECTOR SDK
from svector import SVECTOR, encode_image


def main():
    """Run vision API examples"""
    
    # Initialize client
    client = SVECTOR(api_key=os.getenv("SVECTOR_API_KEY"))
    
    print("🔍 SVECTOR Vision API Examples")
    print("=" * 50)
    
    # Example 1: Analyze image from URL using responses API
    print("\n1. 📸 Analyzing image from URL (Responses API)")
    try:
        response = client.responses.create(
            model="spec-3-turbo",
            input=[{
                "role": "user",
                "content": [
                    {"type": "input_text", "text": "what's in this image?"},
                    {
                        "type": "input_image",
                        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
                    },
                ],
            }],
        )
        print(f"Analysis: {response.output_text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Analyze image from URL using vision API
    print("\n2. 🖼️ Analyzing image from URL (Vision API)")
    try:
        response = client.vision.analyze_from_url(
            image_url="https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg",
            prompt="Describe this logo and what it represents.",
            detail="high"
        )
        print(f"Analysis: {response.analysis}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 3: Analyze image from base64 data
    print("\n3. 📄 Analyzing image from base64 data")
    try:
        # Example with a sample base64 string (you would replace this with actual image data)
        sample_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
        
        response = client.responses.create(
            model="spec-3-turbo",
            input=[
                {
                    "role": "user",
                    "content": [
                        { "type": "input_text", "text": "what's in this image?" },
                        {
                            "type": "input_image",
                            "image_url": f"data:image/png;base64,{sample_base64}",
                        },
                    ],
                }
            ],
        )
        print(f"Analysis: {response.output_text}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 4: Extract text from image (OCR)
    print("\n4. 📝 Extracting text from image (OCR)")
    try:
        response = client.vision.extract_text(
            image_url="https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg"
        )
        print(f"Extracted text: {response.analysis}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 5: Generate accessibility description
    print("\n5. ♿ Generating accessibility description")
    try:
        response = client.vision.describe_for_accessibility(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
        )
        print(f"Accessibility description: {response.analysis}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 6: Detect objects in image
    print("\n6. 🎯 Detecting objects in image")
    try:
        response = client.vision.detect_objects(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            object_types=["people", "trees", "sky", "path", "grass"]
        )
        print(f"Object detection: {response.analysis}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 7: Generate social media caption
    print("\n7. 📱 Generating social media caption")
    try:
        response = client.vision.generate_caption(
            image_url="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            style="casual"
        )
        print(f"Caption: {response.analysis}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 8: Compare multiple images
    print("\n8. 🔄 Comparing multiple images")
    try:
        images = [
            {"url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"},
            {"url": "https://upload.wikimedia.org/wikipedia/commons/3/31/Wiki_logo_Nupedia.jpg"}
        ]
        
        response = client.vision.compare_images(
            images=images,
            prompt="Compare these two images and describe their differences."
        )
        print(f"Comparison: {response.analysis}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
