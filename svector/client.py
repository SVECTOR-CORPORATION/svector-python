"""
SVECTOR API Client - Enhanced with Conversations API

This client provides both traditional Chat Completions and the new Conversations API
that offers a simplified interface with instructions and input parameters.
"""

import asyncio
import json
import os
import time
from pathlib import Path
from typing import (Any, AsyncIterator, BinaryIO, Dict, Iterator, List,
                    Optional, Union)

import aiohttp
import requests

from .conversations import AsyncConversationsAPI, ConversationsAPI
from .errors import (APIError, AuthenticationError, InternalServerError,
                     NotFoundError, PermissionDeniedError, RateLimitError,
                     SVectorError, UnprocessableEntityError)


class SVECTOR:
    """
    SVECTOR API Client with Conversations API
    
    The primary interface for interacting with SVECTOR models is the Conversations API
    which provides a clean interface using instructions and input parameters.
    
    Example:
        client = SVECTOR(api_key="your-api-key")
        
        # Conversations API (Recommended)
        response = client.conversations.create(
            model="spec-3-turbo",
            instructions="You are a helpful assistant.",
            input="What is machine learning?"
        )
        print(response.output)
        
        # Traditional Chat Completions API (Advanced)
        response = client.chat.create(
            model="spec-3-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ]
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://spec-chat.tech",
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True,
        http_client: Optional[requests.Session] = None
    ):
        # Get API key from environment if not provided
        if not api_key:
            api_key = os.environ.get("SVECTOR_API_KEY")
            
        if not api_key:
            raise AuthenticationError("SVECTOR API key is required. Set it via the api_key parameter or SVECTOR_API_KEY environment variable.")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self.http_client = http_client or requests.Session()
        
        # Configure session
        self.http_client.headers.update({
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "svector-python/1.1.0",
            "Content-Type": "application/json"
        })
        
        # Initialize API endpoints
        self.conversations = ConversationsAPI(self)  # API
        self.chat = ChatAPI(self)                    # Traditional API
        self.models = ModelsAPI(self)
        self.files = FilesAPI(self)
        self.knowledge = KnowledgeAPI(self)
        
    def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        stream: bool = False,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ) -> Union[Dict, requests.Response]:
        """
        Make HTTP request with retries and error handling
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request data
            files: Files to upload
            stream: Whether to stream response
            timeout: Request timeout
            max_retries: Maximum retries
            headers: Additional headers
            **kwargs: Additional request parameters
            
        Returns:
            Response data or Response object for streaming
        """
        url = f"{self.base_url}{endpoint}"
        timeout = timeout or self.timeout
        max_retries = max_retries or self.max_retries
        
        # Prepare headers
        req_headers = self.http_client.headers.copy()
        if headers:
            req_headers.update(headers)
            
        # Remove Content-Type for file uploads
        if files:
            req_headers.pop("Content-Type", None)
            
        for attempt in range(max_retries + 1):
            try:
                response = self.http_client.request(
                    method=method.upper(),
                    url=url,
                    json=data if not files else None,
                    data=data if files else None,
                    files=files,
                    headers=req_headers,
                    timeout=timeout,
                    stream=stream,
                    verify=self.verify_ssl,
                    **kwargs
                )
                
                # Handle HTTP errors
                self._handle_response_errors(response)
                
                if stream:
                    return response
                else:
                    return response.json()
                    
            except requests.exceptions.Timeout:
                if attempt == max_retries:
                    raise SVectorError("Request timeout")
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.ConnectionError:
                if attempt == max_retries:
                    raise SVectorError("Connection error")
                time.sleep(2 ** attempt)
            except (AuthenticationError, NotFoundError, PermissionDeniedError, 
                   UnprocessableEntityError, RateLimitError, APIError) as e:
                # Don't retry these errors
                raise e
                
        raise SVectorError("Max retries exceeded")
    
    def _handle_response_errors(self, response: requests.Response):
        """Handle HTTP response errors"""
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
        elif response.status_code >= 500:
            raise APIError("Internal server error", response.status_code)
        elif response.status_code >= 400:
            error_msg = "API error"
            try:
                error_data = response.json()
                error_msg = error_data.get("error", {}).get("message", error_msg)
            except:
                pass
            raise APIError(error_msg, response.status_code)

    # Convenience methods for different HTTP verbs
    def get(self, endpoint: str, **kwargs) -> Dict:
        """Make GET request"""
        return self.request("GET", endpoint, **kwargs)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """Make POST request"""
        return self.request("POST", endpoint, data=data, **kwargs)
    
    def put(self, endpoint: str, data: Optional[Dict] = None, **kwargs) -> Dict:
        """Make PUT request"""
        return self.request("PUT", endpoint, data=data, **kwargs)
    
    def delete(self, endpoint: str, **kwargs) -> Dict:
        """Make DELETE request"""
        return self.request("DELETE", endpoint, **kwargs)


class AsyncSVECTOR:
    """
    Async SVECTOR API Client
    
    Example:
        async def main():
            client = AsyncSVECTOR(api_key="your-api-key")
            response = await client.conversations.create(
                model="spec-3-turbo",
                instructions="You are a helpful assistant.",
                input="Hello!"
            )
            print(response.output)
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://spec-chat.tech",
        timeout: int = 30,
        max_retries: int = 3,
        verify_ssl: bool = True,
        http_client: Optional[aiohttp.ClientSession] = None
    ):
        if not api_key:
            api_key = os.environ.get("SVECTOR_API_KEY")
            
        if not api_key:
            raise AuthenticationError("SVECTOR API key is required.")
            
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.verify_ssl = verify_ssl
        self._http_client = http_client
        self._session_owned = http_client is None
        
        # Initialize API endpoints
        self.conversations = AsyncConversationsAPI(self)
        self.chat = AsyncChatAPI(self)
        self.models = AsyncModelsAPI(self)
        self.files = AsyncFilesAPI(self)
        self.knowledge = AsyncKnowledgeAPI(self)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def close(self):
        """Close the HTTP session"""
        if self._session_owned and self._http_client:
            await self._http_client.close()
            
    @property
    def http_client(self) -> aiohttp.ClientSession:
        """Get or create HTTP client session"""
        if self._http_client is None:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "svector-python/1.1.0",
                "Content-Type": "application/json"
            }
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._http_client = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(verify_ssl=self.verify_ssl)
            )
        return self._http_client
        
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        **kwargs
    ) -> Dict:
        """Make async HTTP request"""
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.max_retries + 1):
            try:
                async with self.http_client.request(
                    method=method.upper(),
                    url=url,
                    json=data,
                    **kwargs
                ) as response:
                    await self._handle_response_errors(response)
                    return await response.json()
                    
            except asyncio.TimeoutError:
                if attempt == self.max_retries:
                    raise SVectorError("Request timeout")
                await asyncio.sleep(2 ** attempt)
            except aiohttp.ClientError:
                if attempt == self.max_retries:
                    raise SVectorError("Connection error")
                await asyncio.sleep(2 ** attempt)
                
    async def _handle_response_errors(self, response: aiohttp.ClientResponse):
        """Handle async response errors"""
        if response.status == 401:
            raise AuthenticationError("Invalid API key", response.status)
        elif response.status == 404:
            raise NotFoundError("Resource not found", response.status)
        elif response.status == 403:
            raise PermissionDeniedError("Permission denied", response.status)
        elif response.status == 422:
            raise UnprocessableEntityError("Validation error", response.status)
        elif response.status == 429:
            raise RateLimitError("Rate limit exceeded", response.status)
        elif response.status >= 500:
            raise APIError("Internal server error", response.status)
        elif response.status >= 400:
            error_msg = "API error"
            try:
                error_data = await response.json()
                error_msg = error_data.get("error", {}).get("message", error_msg)
            except:
                pass
            raise APIError(error_msg, response.status)


class ChatAPI:
    """Chat completions API for advanced role-based conversations"""
    
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
        Create a chat completion using role-based messages
        
        Args:
            model: Model name (e.g., "spec-3-turbo")
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
            
        response = self.client.request(
            "POST", "/api/chat/completions", data=data, stream=stream
        )
        
        if stream:
            return self._stream_response(response)
        else:
            return response
            
    def create_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Iterator[Dict]:
        """Create streaming chat completion"""
        # Remove 'stream' from kwargs to avoid duplicate parameter
        kwargs.pop('stream', None)
        result = self.create(model=model, messages=messages, stream=True, **kwargs)
        # Since we're passing stream=True, the result should be an Iterator
        if hasattr(result, '__iter__') and not isinstance(result, dict):
            return result
        else:
            raise ValueError("Expected streaming response but got non-streaming result")
        
    def create_with_response(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> tuple[Dict, requests.Response]:
        """Create chat completion and return both data and raw response"""
        data = {
            "model": model,
            "messages": messages,
            **kwargs
        }
        
        response = self.client.request(
            "POST", "/api/chat/completions", data=data, stream=False
        )
        # Note: In real implementation, you'd need to modify request method to return raw response
        return response, None  # Placeholder
            
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


class AsyncChatAPI:
    """Async version of ChatAPI"""
    
    def __init__(self, client: AsyncSVECTOR):
        self.client = client
        
    async def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        files: Optional[List[Dict[str, str]]] = None,
        stream: bool = False,
        **kwargs
    ) -> Dict:
        """Async chat completion"""
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            **kwargs
        }
        
        if max_tokens is not None:
            data["max_tokens"] = max_tokens
            
        if files:
            data["files"] = files
            
        return await self.client.request("POST", "/api/chat/completions", data=data)
        
    async def create_stream(
        self,
        model: str,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[Dict]:
        """Async streaming chat completion"""
        # Remove 'stream' from kwargs to avoid duplicate parameter
        kwargs.pop('stream', None)
        
        data = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        # For now, this is a simplified implementation
        # In a real implementation, you'd need proper async streaming
        response = await self.client.request("POST", "/api/chat/completions", data=data)
        
        # This is a simplified version - in reality you'd need to handle async streaming
        if isinstance(response, dict) and "choices" in response:
            yield response
        else:
            # Handle streaming response properly
            yield response


class ModelsAPI:
    """Models API"""
    
    def __init__(self, client: SVECTOR):
        self.client = client
        
    def list(self) -> Dict:
        """List available models"""
        return self.client.get("/api/models")


class AsyncModelsAPI:
    """Async Models API"""
    
    def __init__(self, client: AsyncSVECTOR):
        self.client = client
        
    async def list(self) -> Dict:
        """List available models"""
        return await self.client.request("GET", "/api/models")


class FilesAPI:
    """Files API for document processing and RAG"""
    
    def __init__(self, client: SVECTOR):
        self.client = client
        
    def create(
        self,
        file: Union[str, bytes, BinaryIO, Path],
        purpose: str = "default",
        filename: Optional[str] = None
    ) -> Dict:
        """
        Upload a file for RAG or analysis
        
        Args:
            file: File path, bytes, Path object, or file-like object
            purpose: File purpose (default: "default")
            filename: Optional filename override
            
        Returns:
            Dict with file upload response including file_id
        """
        files_data = {}
        data = {"purpose": purpose}
        
        if isinstance(file, (str, Path)):
            # File path
            file_path = Path(file)
            with open(file_path, 'rb') as f:
                files_data = {
                    "file": (filename or file_path.name, f, "application/octet-stream")
                }
                return self.client.request(
                    "POST", "/api/v1/files/", data=data, files=files_data
                )
        elif isinstance(file, bytes):
            # Bytes
            files_data = {
                "file": (filename or "file", file, "application/octet-stream")
            }
            return self.client.request(
                "POST", "/api/v1/files/", data=data, files=files_data
            )
        else:
            # File-like object
            files_data = {
                "file": (filename or "file", file, "application/octet-stream")
            }
            return self.client.request(
                "POST", "/api/v1/files/", data=data, files=files_data
            )


class AsyncFilesAPI:
    """Async Files API"""
    
    def __init__(self, client: AsyncSVECTOR):
        self.client = client
        
    async def create(
        self,
        file: Union[str, bytes, Path],
        purpose: str = "default",
        filename: Optional[str] = None
    ) -> Dict:
        """Async file upload"""
        # Simplified async implementation
        if isinstance(file, (str, Path)):
            with open(file, 'rb') as f:
                file_data = f.read()
        elif isinstance(file, bytes):
            file_data = file
        else:
            file_data = file.read()
            
        # This would need proper multipart upload implementation
        # Placeholder for now
        return {"file_id": "async-placeholder", "purpose": purpose}


class KnowledgeAPI:
    """Knowledge collections API"""
    
    def __init__(self, client: SVECTOR):
        self.client = client
        
    def add_file(self, collection_id: str, file_id: str) -> Dict:
        """Add a file to a knowledge collection"""
        data = {"file_id": file_id}
        return self.client.post(f"/api/v1/knowledge/{collection_id}/file/add", data=data)


class AsyncKnowledgeAPI:
    """Async Knowledge collections API"""
    
    def __init__(self, client: AsyncSVECTOR):
        self.client = client
        
    async def add_file(self, collection_id: str, file_id: str) -> Dict:
        """Add a file to a knowledge collection"""
        data = {"file_id": file_id}
        return await self.client.request(
            "POST", f"/api/v1/knowledge/{collection_id}/file/add", data=data
        )
