#!/usr/bin/env python3
"""
SVECTOR Python SDK - Vision with File Upload Example

This example demonstrates how to upload a file and then analyze it with vision.
"""

import base64
import os
from pathlib import Path

# Import SVECTOR SDK
from svector import SVECTOR


def encode_image(image_path):
    """Encode an image file to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def main():
    """Run file upload and vision example"""
    
    # Initialize client
    client = SVECTOR(api_key=os.getenv("SVECTOR_API_KEY"))
    
    print("📁 SVECTOR File Upload + Vision Example")
    print("=" * 50)
    
    # Example 1: Upload file and analyze with file ID
    print("\n1. 📤 Upload image file and analyze")
    
    # Note: You would replace this with an actual image file path
    example_image_path = "path_to_your_image.jpg"
    
    if Path(example_image_path).exists():
        try:
            # Upload the file
            print(f"Uploading {example_image_path}...")
            file_result = client.files.create(
                file=open(example_image_path, "rb"),
                purpose="vision"
            )
            file_id = file_result["id"]
            print(f"File uploaded with ID: {file_id}")
            
            # Analyze using file ID
            response = client.responses.create(
                model="spec-3-turbo",
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "what's in this image?"},
                        {
                            "type": "input_image",
                            "file_id": file_id,
                        },
                    ],
                }],
            )
            print(f"Analysis: {response.output_text}")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"File not found: {example_image_path}")
        print("Please update the example_image_path variable with a valid image file path")
    
    # Example 2: Base64 encoding and analysis
    print("\n2. 🔤 Base64 encoding and analysis")
    
    if Path(example_image_path).exists():
        try:
            # Encode image to base64
            base64_image = encode_image(example_image_path)
            print(f"Image encoded to base64 ({len(base64_image)} characters)")
            
            # Analyze using base64 data
            response = client.responses.create(
                model="spec-3-turbo",
                input=[
                    {
                        "role": "user",
                        "content": [
                            { "type": "input_text", "text": "what's in this image?" },
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{base64_image}",
                            },
                        ],
                    }
                ],
            )
            print(f"Analysis: {response.output_text}")
            
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"File not found: {example_image_path}")
    
    # Example 3: Multiple analysis types on the same image
    print("\n3. 🔍 Multiple analysis types")
    
    image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
    
    try:
        # Regular analysis
        print("\n   📸 General Analysis:")
        response = client.vision.analyze_from_url(
            image_url=image_url,
            prompt="Describe this image in detail."
        )
        print(f"   {response.analysis[:200]}...")
        
        # OCR
        print("\n   📝 Text Extraction:")
        response = client.vision.extract_text(image_url=image_url)
        print(f"   {response.analysis}")
        
        # Accessibility description
        print("\n   ♿ Accessibility Description:")
        response = client.vision.describe_for_accessibility(image_url=image_url)
        print(f"   {response.analysis[:200]}...")
        
        # Professional caption
        print("\n   💼 Professional Caption:")
        response = client.vision.generate_caption(
            image_url=image_url,
            style="professional"
        )
        print(f"   {response.analysis}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
