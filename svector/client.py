"""
SVECTOR API Client
"""

import json
import time
from typing import Any, BinaryIO, Dict, Iterator, List, Optional, Union

import requests

from .errors import (APIError, AuthenticationError, NotFoundError,
                     PermissionDeniedError, RateLimitError, SVectorError,
                     UnprocessableEntityError)


class SVECTOR:
    """
    SVECTOR API Client
    
    Example:
        client = SVECTOR(api_key="your-api-key")
        response = client.chat.create(
            model="spec-3-turbo:latest",
            messages=[{"role": "user", "content": "Hello!"}]
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://spec-chat.tech",
        timeout: int = 30,
        max_retries: int = 3
    ):
        if not api_key:
            raise AuthenticationError("API key is required")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Initialize API endpoints
        self.chat = ChatAPI(self)
        self.models = ModelsAPI(self)
        self.files = FilesAPI(self)
        
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        stream: bool = False,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request with retries and error handling"""
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "svector-python/1.0.0"
        }
        
        if not files:
            headers["Content-Type"] = "application/json"
            
        for attempt in range(self.max_retries + 1):
            try:
                if method.upper() == "GET":
                    response = requests.get(
                        url, headers=headers, timeout=self.timeout, 
                        stream=stream, **kwargs
                    )
                elif method.upper() == "POST":
                    if files:
                        response = requests.post(
                            url, headers={k: v for k, v in headers.items() if k != "Content-Type"},
                            data=data, files=files, timeout=self.timeout, **kwargs
                        )
                    else:
                        response = requests.post(
                            url, headers=headers, json=data, 
                            timeout=self.timeout, stream=stream, **kwargs
                        )
                else:
                    raise ValueError(f"Unsupported method: {method}")
                    
                # Handle HTTP errors
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key", response.status_code)
                elif response.status_code == 404:
                    raise NotFoundError("Resource not found", response.status_code)
                elif response.status_code == 403:
                    raise PermissionDeniedError("Permission denied", response.status_code)
                elif response.status_code == 422:
                    raise UnprocessableEntityError("Validation error", response.status_code)
                elif response.status_code == 429:
                    raise RateLimitError("Rate limit exceeded", response.status_code)
                elif response.status_code >= 400:
                    error_msg = "API error"
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("error", {}).get("message", error_msg)
                    except:
                        pass
                    raise APIError(error_msg, response.status_code)
                    
                return response
                
            except requests.exceptions.Timeout:
                if attempt == self.max_retries:
                    raise SVectorError("Request timeout")
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.ConnectionError:
                if attempt == self.max_retries:
                    raise SVectorError("Connection error")
                time.sleep(2 ** attempt)
            except (AuthenticationError, NotFoundError, PermissionDeniedError, 
                   UnprocessableEntityError, RateLimitError) as e:
                # Don't retry these errors
                raise e
                
        raise SVectorError("Max retries exceeded")


class ChatAPI:
    """Chat completions API"""
    
    def __init__(self, client: SVECTOR):
        self.client = client
        
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        files: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[Dict, Iterator[Dict]]:
        """
        Create a chat completion
        
        Args:
            model: Model name (e.g., "spec-3-turbo:latest")
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum tokens to generate
            files: List of file references for RAG
            stream: Whether to stream the response
            
        Returns:
            Dict with response data or Iterator for streaming
        """
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            **kwargs
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
            
        if files:
            data["files"] = files
            
        response = self.client._make_request(
            "POST", "/api/chat/completions", data=data, stream=stream
        )
        
        if stream:
            return self._stream_response(response)
        else:
            return response.json()
            
    def _stream_response(self, response: requests.Response) -> Iterator[Dict]:
        """Parse streaming response"""
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data = line[6:]
                    if data.strip() == '[DONE]':
                        break
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        continue


class ModelsAPI:
    """Models API"""
    
    def __init__(self, client: SVECTOR):
        self.client = client
        
    def list(self) -> Dict:
        """List available models"""
        response = self.client._make_request("GET", "/api/models")
        return response.json()


class FilesAPI:
    """Files API for RAG"""
    
    def __init__(self, client: SVECTOR):
        self.client = client
        
    def create(
        self,
        file: Union[str, bytes, BinaryIO],
        purpose: str = "rag",
        filename: Optional[str] = None
    ) -> Dict:
        """
        Upload a file for RAG
        
        Args:
            file: File path, bytes, or file-like object
            purpose: File purpose (default: "rag")
            filename: Optional filename
            
        Returns:
            Dict with file upload response
        """
        files_data = {}
        data = {"purpose": purpose}
        
        if isinstance(file, str):
            # File path
            with open(file, 'rb') as f:
                files_data = {"file": (filename or file, f, "application/octet-stream")}
                response = self.client._make_request(
                    "POST", "/api/files", data=data, files=files_data
                )
        elif isinstance(file, bytes):
            # Bytes
            files_data = {"file": (filename or "file", file, "application/octet-stream")}
            response = self.client._make_request(
                "POST", "/api/files", data=data, files=files_data
            )
        else:
            # File-like object
            files_data = {"file": (filename or "file", file, "application/octet-stream")}
            response = self.client._make_request(
                "POST", "/api/files", data=data, files=files_data
            )
            
        return response.json()
