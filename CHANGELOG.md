# SVECTOR Python SDK Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-06-17

### Added
- Initial release of SVECTOR Python SDK
- Complete chat completions API with streaming support
- File upload and RAG (Retrieval Augmented Generation) capabilities
- Models API for listing available models
- Comprehensive error handling with specific error types
- Command-line interface (CLI) for easy interaction
- Support for multiple file upload methods (path, bytes, file object)
- Multi-turn conversation support
- Automatic retry logic with exponential backoff
- Type hints for better developer experience
- Comprehensive documentation and examples

### Features
- **Chat API**: Complete chat completions with customizable parameters
- **Streaming**: Real-time response streaming via Server-Sent Events
- **File Upload**: Support for various file formats for RAG functionality
- **Error Handling**: Specific error classes for different API scenarios
- **CLI Tool**: Full-featured command-line interface
- **Python 3.8+**: Support for modern Python versions
- **Production Ready**: Robust error handling and retry mechanisms

### CLI Commands
- `svector chat` - Send chat messages
- `svector stream` - Stream responses in real-time
- `svector models` - List available models
- `svector config` - Manage API key configuration
- `svector file upload` - Upload files for RAG
- `svector ask` - Ask questions about uploaded files

### API Coverage
- Chat completions with parameters (temperature, max_tokens, etc.)
- Streaming responses
- File uploads for RAG functionality
- Model listing
- Multi-file RAG queries
- Response metadata access

### Dependencies
- `requests>=2.25.0` - HTTP client
- `typing-extensions>=4.0.0` - Type hints for Python <3.10

---

## Installation

```bash
pip install svector
```

## Quick Start

```python
from svector import SVECTOR

client = SVECTOR(api_key="your-api-key")
response = client.chat.create(
    model="spec-3-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

For more information, visit: https://www.svector.co.in
