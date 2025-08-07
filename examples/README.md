# SVECTOR Python SDK Examples

This directory contains comprehensive examples and tests for the SVECTOR Python SDK, demonstrating all available features including conversations, chat completions, vision analysis, and more.

## 📁 File Overview

### Vision API Examples
- **`examples_vision_comprehensive.py`** - Complete vision API demonstration with all features
- **`examples_exact_format.py`** - Exact format examples matching Node.js/JSR SDK patterns
- **`examples_vision.py`** - Basic vision API examples
- **`examples_vision_file.py`** - File upload and vision analysis examples

### General Examples
- **`examples_comprehensive.py`** - Complete SDK demonstration with all APIs
- **`examples.py`** - Basic usage examples and getting started

### Tests
- **`test_vision_quick.py`** - Quick vision API functionality test
- **`test_streaming.py`** - Streaming functionality test
- **`test_final.py`** - Comprehensive test suite
- **`test_import.py`** - Import and basic functionality test

## 🚀 Quick Start

### Prerequisites

```bash
pip install svector-sdk
export SVECTOR_API_KEY="your-api-key-here"
```

### Running Examples

```bash
# Run comprehensive vision examples
python examples/examples_vision_comprehensive.py

# Run exact format examples (matching Node.js patterns)
python examples/examples_exact_format.py

# Run quick vision test
python examples/test_vision_quick.py

# Run streaming test
python examples/test_streaming.py
```

## 📸 Vision API Examples

### 1. Basic Image Analysis

```python
from svector import SVECTOR

client = SVECTOR()

# Analyze image from URL
response = client.vision.analyze_from_url(
    image_url="https://example.com/image.jpg",
    prompt="What do you see in this image?",
    detail="high"
)
print(response.analysis)
```

### 2. Responses API Format (Node.js Compatible)

```python
# Using responses.create format
response = client.responses.create(
    model="spec-3-turbo",
    input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": "what's in this image?"},
            {
                "type": "input_image",
                "image_url": "https://example.com/image.jpg",
            },
        ],
    }],
)
print(response.output_text)
```

### 3. Base64 Image Analysis

```python
import base64

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# Getting the Base64 string
base64_image = encode_image("path_to_your_image.jpg")

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
```

### 4. File Upload and Analysis

```python
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
```

## 🔧 Advanced Vision Features

### OCR (Text Extraction)

```python
response = client.vision.extract_text(
    image_url="https://example.com/document.jpg"
)
print(f"Extracted text: {response.analysis}")
```

### Object Detection

```python
response = client.vision.detect_objects(
    image_url="https://example.com/scene.jpg",
    object_types=["cars", "people", "buildings"]
)
print(f"Detected objects: {response.analysis}")
```

### Image Comparison

```python
images = [
    {"url": "https://example.com/image1.jpg"},
    {"url": "https://example.com/image2.jpg"}
]

response = client.vision.compare_images(
    images=images,
    prompt="Compare these images and describe differences"
)
print(response.analysis)
```

### Confidence Scoring

```python
result = client.vision.analyze_with_confidence(
    image_url="https://example.com/image.jpg",
    prompt="Analyze this image"
)
print(f"Analysis: {result['analysis']}")
print(f"Confidence: {result['confidence']}%")
```

### Batch Processing

```python
images = [
    {"image_url": "https://example.com/1.jpg", "prompt": "Describe this"},
    {"image_url": "https://example.com/2.jpg", "prompt": "What's here?"}
]

results = client.vision.batch_analyze(images, delay=1.0)
for i, result in enumerate(results):
    print(f"Image {i+1}: {result['analysis']}")
```

## 💬 Conversations API Examples

### Basic Conversation

```python
response = client.conversations.create(
    model="spec-3-turbo",
    instructions="You are a helpful AI assistant.",
    input="Explain quantum computing in simple terms."
)
print(response.output)
```

### Streaming Conversation

```python
stream = client.conversations.create_stream(
    model="spec-3-turbo",
    instructions="You are a creative writer.",
    input="Write a short poem about technology."
)

for event in stream:
    if not event.done:
        print(event.content, end="", flush=True)
```

## 🔀 Chat Completions API Examples

### Role-based Chat

```python
response = client.chat.create(
    model="spec-3-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is machine learning?"}
    ]
)
print(response["choices"][0]["message"]["content"])
```

## 📁 File Management Examples

### Upload File

```python
with open("document.pdf", "rb") as f:
    file_response = client.files.create(
        file=f,
        purpose="default"
    )
print(f"File ID: {file_response['file_id']}")
```

## 🚨 Error Handling Examples

```python
from svector import APIError, AuthenticationError, RateLimitError

try:
    response = client.vision.analyze_from_url(
        image_url="https://example.com/image.jpg"
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except APIError as e:
    print(f"API error: {e}")
```

## 🔧 Utility Functions

```python
from svector import encode_image, create_data_url

# Encode image to base64
base64_data = encode_image("path/to/image.jpg")

# Create data URL
data_url = create_data_url(base64_data, "image/jpeg")
```

## 📋 Best Practices

1. **Always handle errors** - Wrap API calls in try-catch blocks
2. **Use appropriate timeouts** - Set reasonable timeouts for vision requests
3. **Optimize image sizes** - Smaller images process faster
4. **Use specific prompts** - Better prompts yield better results
5. **Handle rate limits** - Add delays between batch requests
6. **Choose the right detail level** - Use "high" for complex analysis, "low" for speed

## 🔍 Troubleshooting

### Common Issues

1. **Timeout errors**: Reduce image size or set `detail="low"`
2. **Authentication errors**: Check your API key
3. **Rate limiting**: Add delays between requests
4. **Large images**: Use file upload method instead of base64

### Debug Mode

Set environment variable for detailed logging:
```bash
export SVECTOR_DEBUG=1
python your_script.py
```

## 📚 Additional Resources

- [SVECTOR Dashboard](https://svector.co.in) - Get your API key
- [Python SDK Documentation](../README.md) - Complete documentation
- [API Reference](https://docs.svector.co.in) - Full API documentation

## 🆘 Support

If you encounter issues:
1. Check the examples in this directory
2. Review the main README.md
3. Contact support at support@svector.co.in
