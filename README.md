# SVECTOR Python SDK

[![PyPI version](https://badge.fury.io/py/svector.svg)](https://badge.fury.io/py/svector)
[![Python Support](https://img.shields.io/pypi/pyversions/svector.svg)](https://pypi.org/project/svector/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The official Python SDK for **SVECTOR AI Models**. Build powerful AI applications with advanced conversational AI and language models.

## 🚀 Installation

```bash
pip install svector
```

## 🎯 Quick Start

### Basic Usage

```python
from svector import SVECTOR

# Initialize the client
client = SVECTOR(api_key="your-api-key-here")

# Simple chat completion
response = client.chat.create(
    model="spec-3-turbo:latest",
    messages=[
        {"role": "user", "content": "What is artificial intelligence?"}
    ]
)

print(response["choices"][0]["message"]["content"])
```

### Streaming Responses

```python
# Stream responses in real-time
stream = client.chat.create(
    model="spec-3-turbo:latest",
    messages=[
        {"role": "user", "content": "Write a poem about technology"}
    ],
    stream=True
)

for event in stream:
    if event.get("choices") and event["choices"][0].get("delta", {}).get("content"):
        print(event["choices"][0]["delta"]["content"], end="", flush=True)
```

### File Upload and RAG

```python
# Upload a file for RAG
file_response = client.files.create("document.pdf", purpose="rag")
file_id = file_response["file_id"]

# Ask questions about the uploaded file
response = client.chat.create(
    model="spec-3-turbo:latest",
    messages=[
        {"role": "user", "content": "Summarize this document"}
    ],
    files=[{"type": "file", "id": file_id}]
)

print(response["choices"][0]["message"]["content"])
```

## 🖥️ Command Line Interface

SVECTOR also provides a powerful CLI:

```bash
# Set up your API key
svector config set-key your-api-key-here

# Start chatting
svector chat "Hello, SVECTOR!"

# Stream responses
svector stream "Write a poem about AI"

# List available models
svector models

# Upload files for RAG
svector file upload document.pdf

# Ask questions about files
svector ask "Summarize this document" --file file-123
```

## 📚 API Reference

### SVECTOR Client

```python
client = SVECTOR(
    api_key="your-api-key",           # Required: Your SVECTOR API key
    base_url="https://api.svector.co.in",  # Optional: Custom API base URL
    timeout=30,                       # Optional: Request timeout in seconds
    max_retries=3                     # Optional: Max retry attempts
)
```

### Chat Completions

```python
response = client.chat.create(
    model="spec-3-turbo:latest",      # Required: Model name
    messages=[                        # Required: List of messages
        {"role": "user", "content": "Hello"}
    ],
    temperature=0.7,                  # Optional: 0.0 to 2.0
    max_tokens=150,                   # Optional: Max tokens to generate
    files=[                           # Optional: Files for RAG
        {"type": "file", "id": "file-123"}
    ],
    stream=False                      # Optional: Enable streaming
)
```

### Models API

```python
# List available models
models = client.models.list()
print(models["models"])
```

### Files API

```python
# Upload from file path
response = client.files.create("path/to/file.pdf", purpose="rag")

# Upload from bytes
with open("file.pdf", "rb") as f:
    response = client.files.create(f.read(), purpose="rag", filename="file.pdf")

# Upload from file object
with open("file.pdf", "rb") as f:
    response = client.files.create(f, purpose="rag", filename="file.pdf")
```

## 🔧 Advanced Examples

### Multi-turn Conversation

```python
conversation = [
    {"role": "system", "content": "You are a helpful programming assistant."},
    {"role": "user", "content": "How do I create a function in Python?"},
]

response = client.chat.create(
    model="spec-3-turbo:latest",
    messages=conversation,
    temperature=0.3
)

# Add the AI response to conversation history
conversation.append({
    "role": "assistant", 
    "content": response["choices"][0]["message"]["content"]
})

# Continue the conversation
conversation.append({
    "role": "user", 
    "content": "Can you show me an example?"
})

response = client.chat.create(
    model="spec-3-turbo:latest",
    messages=conversation
)
```

### Multi-file RAG

```python
# Upload multiple files
file1 = client.files.create("technical_specs.pdf")
file2 = client.files.create("user_manual.pdf")

# Query across multiple documents
response = client.chat.create(
    model="spec-3-turbo:latest",
    messages=[
        {"role": "user", "content": "Compare the technical specifications with the user manual"}
    ],
    files=[
        {"type": "file", "id": file1["file_id"]},
        {"type": "file", "id": file2["file_id"]}
    ]
)
```

### Error Handling

```python
from svector import SVECTOR, AuthenticationError, RateLimitError, APIError

try:
    client = SVECTOR(api_key="invalid-key")
    response = client.chat.create(
        model="spec-3-turbo:latest",
        messages=[{"role": "user", "content": "Hello"}]
    )
except AuthenticationError:
    print("Invalid API key")
except RateLimitError:
    print("Rate limit exceeded")
except APIError as e:
    print(f"API error: {e}")
```

## 🌟 Features

- **✅ Complete API Coverage**: Chat completions, streaming, file upload, RAG
- **✅ Type Safety**: Full type hints for better development experience
- **✅ Error Handling**: Comprehensive error types and retry logic
- **✅ Streaming Support**: Real-time response streaming
- **✅ File Upload**: Support for various file formats and RAG
- **✅ CLI Interface**: Command-line tool for quick interactions
- **✅ Production Ready**: Robust error handling and retry mechanisms

## 🔑 Authentication

Get your API key from the [SVECTOR Dashboard](https://www.svector.co.in/dashboard).

Set it as an environment variable:

```bash
export SVECTOR_API_KEY="your-api-key-here"
```

Or pass it directly to the client:

```python
client = SVECTOR(api_key="your-api-key-here")
```

## 🌍 Supported Models

- `spec-3-turbo:latest` - General purpose model with excellent performance
- `spec-3-pro:latest` - Advanced reasoning model for complex tasks

Get the latest list:

```python
models = client.models.list()
```

## 📋 Requirements

- Python 3.8+
- `requests` library (automatically installed)

## 🤝 Support

- **Documentation**: [https://www.svector.co.in/docs](https://www.svector.co.in/docs)
- **Email**: support@svector.co.in
- **Issues**: [GitHub Issues](https://github.com/svector-corporation/svector-python/issues)

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🚀 Getting Started

1. **Install the package**:
   ```bash
   pip install svector
   ```

2. **Get your API key**: Visit [https://www.svector.co.in](https://www.svector.co.in)

3. **Start building**:
   ```python
   from svector import SVECTOR
   
   client = SVECTOR(api_key="your-key")
   response = client.chat.create(
       model="spec-3-turbo:latest",
       messages=[{"role": "user", "content": "Hello, SVECTOR!"}]
   )
   ```

---

**Built with ❤️ by the SVECTOR Team**
