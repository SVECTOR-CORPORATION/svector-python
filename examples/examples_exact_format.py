#!/usr/bin/env python3
"""
SVECTOR Vision API Examples - Matching Node.js/JSR SDK functionality

This file demonstrates the exact patterns requested in the user prompt:
1. responses.create with image URL
2. responses.create with base64 image  
3. responses.create with file ID

Setup:
    pip install svector-sdk
    export SVECTOR_API_KEY="your-api-key-here"
"""

import base64
import os

from svector import SVECTOR


def main():
    """Run the three main vision examples"""
    # Initialize client
    client = SVECTOR(api_key=os.getenv("SVECTOR_API_KEY"))
    
    print("🚀 SVECTOR Python Vision Examples")
    print("=" * 40)
    
    # Example 1: Image URL
    example_1_image_url(client)
    
    # Example 2: Base64 image
    example_2_base64_image(client)
    
    # Example 3: File ID
    example_3_file_id(client)
    
    print("\n✅ All examples completed!")


def example_1_image_url(client: SVECTOR):
    """Example 1: Using responses.create with image URL"""
    print("\n1. 🔗 Image URL Example")
    print("-" * 30)
    
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
        
        print(f"✅ Success!")
        print(f"Output: {response.output_text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def example_2_base64_image(client: SVECTOR):
    """Example 2: Using responses.create with base64 image"""
    print("\n2. 📁 Base64 Image Example")
    print("-" * 30)
    
    # Function to encode the image
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    try:
        # For this example, we'll create a minimal test image or use a placeholder
        # In real usage, you'd specify your actual image path
        image_path = "path_to_your_image.jpg"  # Replace with actual path
        
        # For demo purposes, we'll use a tiny base64 encoded image
        # This is a 1x1 pixel transparent PNG
        base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
        
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
        
        print(f"✅ Success!")
        print(f"Output: {response.output_text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Show the pattern for real usage
    print("\n📝 Real Usage Pattern:")
    print("""
# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Path to your image
image_path = "path_to_your_image.jpg"

# Getting the Base64 string
base64_image = encode_image(image_path)

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

print(response.output_text)
    """)


def example_3_file_id(client: SVECTOR):
    """Example 3: Using responses.create with file ID"""
    print("\n3. 📤 File ID Example")
    print("-" * 30)
    
    # Function to create a file with the Files API
    def create_file(file_path):
        with open(file_path, "rb") as file_content:
            result = client.files.create(
                file=file_content,
                purpose="vision",
            )
            return result["file_id"]  # Note: Using dict access for file_id

    try:
        # For demo, we'll show the pattern but not actually upload
        print("📝 Usage Pattern:")
        print("""
# Function to create a file with the Files API
def create_file(file_path):
    with open(file_path, "rb") as file_content:
        result = client.files.create(
            file=file_content,
            purpose="vision",
        )
        return result["file_id"]

# Getting the file ID
file_id = create_file("path_to_your_image.jpg")

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

print(response.output_text)
        """)
        
        # If you want to test with an actual file, uncomment below:
        # file_id = create_file("path_to_your_image.jpg")
        # response = client.responses.create(...)
        
    except Exception as e:
        print(f"❌ Error: {e}")


def show_additional_examples():
    """Show additional vision capabilities"""
    print("\n🔧 Additional Vision Capabilities")
    print("-" * 40)
    
    print("""
# Direct vision API methods
from svector import SVECTOR

client = SVECTOR()

# Analyze from URL
response = client.vision.analyze_from_url(
    image_url="https://example.com/image.jpg",
    prompt="Describe this image in detail",
    detail="high"
)

# Analyze from base64
response = client.vision.analyze_from_base64(
    base64_data=base64_image,
    prompt="What objects can you identify?"
)

# Analyze from file ID
response = client.vision.analyze_from_file_id(
    file_id=file_id,
    prompt="Extract all text from this image"
)

# OCR (text extraction)
response = client.vision.extract_text(
    image_url="https://example.com/document.jpg"
)

# Object detection
response = client.vision.detect_objects(
    image_url="https://example.com/scene.jpg",
    object_types=["cars", "people", "buildings"]
)

# Accessibility description
response = client.vision.describe_for_accessibility(
    image_url="https://example.com/chart.jpg"
)

# Image comparison
images = [
    {"url": "https://example.com/image1.jpg"},
    {"url": "https://example.com/image2.jpg"}
]
response = client.vision.compare_images(
    images=images,
    prompt="Compare these images"
)

# Batch processing
images = [
    {"image_url": "https://example.com/1.jpg", "prompt": "Describe this"},
    {"image_url": "https://example.com/2.jpg", "prompt": "What's here?"}
]
results = client.vision.batch_analyze(images)

# Confidence scoring
result = client.vision.analyze_with_confidence(
    image_url="https://example.com/image.jpg"
)
print(f"Analysis: {result['analysis']}")
print(f"Confidence: {result['confidence']}%")
    """)


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("SVECTOR_API_KEY"):
        print("❌ Please set SVECTOR_API_KEY environment variable")
        print("   export SVECTOR_API_KEY='your-api-key-here'")
        exit(1)
    
    main()
    show_additional_examples()
