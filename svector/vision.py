"""
SVECTOR Vision API

Provides image analysis capabilities using SVECTOR's vision models.
Supports image URL, base64, and file ID inputs for comprehensive image understanding.
"""

import base64
import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import requests

from .errors import (APIConnectionTimeoutError, APIError, AuthenticationError,
                     RateLimitError, SVECTORError)


class VisionResponse:
    """Response from vision analysis"""
    
    def __init__(self, data: Dict[str, Any]):
        self.analysis = data.get("analysis", "")
        self.output_text = data.get("analysis", "")  # Alias for compatibility
        self.usage = data.get("usage", {})
        self.request_id = data.get("_request_id")
        self._raw_data = data

    def __str__(self):
        return self.analysis


class VisionAPI:
    """
    Vision API for SVECTOR
    
    Provides comprehensive image analysis capabilities including:
    - Image analysis from URLs, base64 data, or file IDs
    - Object detection and recognition
    - Text extraction (OCR)
    - Image comparison
    - Accessibility descriptions
    - Custom prompts for specific analysis tasks
    """
    
    def __init__(self, client):
        self.client = client
        
    def _make_vision_request(
        self,
        chat_request: Dict[str, Any],
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Make a direct API call to SVECTOR vision endpoint
        """
        endpoints = [
            f"{self.client.base_url}/api/chat/completions",
            "https://spec-chat.tech/api/chat/completions",
        ]
        
        headers = {
            "Authorization": f"Bearer {self.client.api_key}",
            "Content-Type": "application/json"
        }
        
        timeout = timeout or 60  # Default 60 second timeout for vision
        max_retries = max_retries or 2
        
        print(f"🔍 Vision API: Starting request with {timeout}s timeout...")
        
        for endpoint_index, endpoint in enumerate(endpoints):
            
            for retry in range(max_retries):
                
                try:
                    request_start = time.time()
                    
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json=chat_request,
                        timeout=timeout,
                        verify=self.client.verify_ssl
                    )
                    
                    request_duration = time.time() - request_start
                    print(f"⚡ Request completed in {request_duration:.2f}s")
                    
                    if not response.ok:
                        error_text = response.text
                        print(f"HTTP {response.status_code}: {error_text}")
                        
                        # Handle specific HTTP status codes
                        if response.status_code == 504:
                            raise APIConnectionTimeoutError(
                                "Gateway timeout: The image processing took too long. "
                                "Try using a smaller image or 'low' detail setting."
                            )
                        elif response.status_code == 413:
                            raise APIError(
                                "Image too large: Please use a smaller image file or reduce the image resolution."
                            )
                        elif response.status_code == 429:
                            raise RateLimitError("Rate limit exceeded: Please wait before making another request.")
                        elif response.status_code >= 400 and response.status_code < 500:
                            raise APIError(f"HTTP {response.status_code}: {error_text}")
                        
                        # For 5xx errors (server errors like 524 timeout), retry with next endpoint or retry
                        if response.status_code >= 500:
                            is_last_retry = retry == max_retries - 1
                            is_last_endpoint = endpoint_index == len(endpoints) - 1
                            
                            if is_last_retry and is_last_endpoint:
                                raise APIError(f"HTTP {response.status_code}: {error_text}")
                            
                            # If not last retry or not last endpoint, continue to retry
                            continue
                        
                        # For other errors, treat as retry-able
                        if retry == max_retries - 1:
                            raise APIError(f"HTTP {response.status_code}: {error_text}")
                        continue
                    
                    result = response.json()
                    return result
                    
                except requests.exceptions.Timeout:
                    is_last_retry = retry == max_retries - 1
                    is_last_endpoint = endpoint_index == len(endpoints) - 1
                    
                    if is_last_retry and is_last_endpoint:
                        raise APIConnectionTimeoutError(
                            f"Vision API request timed out after {timeout}s. "
                            "This may be due to a large image or server overload. "
                            "Try using a smaller image, setting detail to 'low', or increasing the timeout."
                        )
                    
                except requests.exceptions.ConnectionError as e:
                    is_last_retry = retry == max_retries - 1
                    is_last_endpoint = endpoint_index == len(endpoints) - 1
                    
                    if is_last_retry and is_last_endpoint:
                        raise SVECTORError("Network error: Unable to connect to vision API. Please check your internet connection.")
                    
                except Exception as e:
                    is_last_retry = retry == max_retries - 1
                    is_last_endpoint = endpoint_index == len(endpoints) - 1
                    
                    if is_last_retry and is_last_endpoint:
                        raise SVECTORError(f"Vision API request failed: {e}")
                
                # Exponential backoff for retries
                if retry < max_retries - 1 or endpoint_index < len(endpoints) - 1:
                    delay = min(1000 * (2 ** retry), 5000) / 1000  # Convert to seconds
                    time.sleep(delay)
        
        raise SVECTORError("Vision API request failed after multiple retries on all endpoints")
    
    def analyze(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        file_id: Optional[str] = None,
        prompt: Optional[str] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        detail: str = "auto",
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> VisionResponse:
        """
        Analyze an image using SVECTOR's vision capabilities
        
        Args:
            image_url: URL of the image to analyze
            image_base64: Base64 encoded image data
            file_id: File ID from files API
            prompt: Custom prompt for analysis
            model: Model to use for analysis
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            detail: Image detail level ('low', 'high', 'auto')
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            
        Returns:
            VisionResponse with analysis results
            
        Example:
            response = client.vision.analyze(
                image_url="https://example.com/image.jpg",
                prompt="What do you see in this image?"
            )
            print(response.analysis)
        """
        if not any([image_url, image_base64, file_id]):
            raise ValueError("Must provide one of: image_url, image_base64, or file_id")
        
        message_content: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": prompt or "Analyze this image and describe what you see in detail."
            }
        ]
        
        if image_url:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": image_url,
                    "detail": detail
                }
            })
        elif image_base64:
            data_url = image_base64 if image_base64.startswith('data:') else f"data:image/jpeg;base64,{image_base64}"
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": data_url,
                    "detail": detail
                }
            })
        elif file_id:
            message_content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"file://{file_id}",
                    "detail": detail
                }
            })
        
        chat_request = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": message_content
            }],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = self._make_vision_request(chat_request, timeout, max_retries)
            
            analysis = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not analysis:
                raise SVECTORError("No analysis content returned from API")
            
            return VisionResponse({
                "analysis": analysis,
                "usage": response.get("usage", {}),
                "_request_id": response.get("_request_id")
            })
            
        except APIConnectionTimeoutError as e:
            # Re-throw timeout errors with additional context
            raise APIConnectionTimeoutError(
                f"{e}\n\nTroubleshooting tips:\n"
                "• Try reducing image size or resolution\n"
                "• Use detail: 'low' instead of 'high'\n"
                "• Check if the image URL is accessible\n"
                "• Consider using a different image format"
            )
        except Exception as e:
            error_message = str(e)
            
            # More specific error handling
            if "504" in error_message or "Gateway timeout" in error_message:
                raise APIConnectionTimeoutError(
                    "Image processing timed out. The image may be too large or complex. "
                    "Try using a smaller image or setting detail to 'low'."
                )
            elif "413" in error_message or "too large" in error_message:
                raise APIError("Image too large. Please use a smaller image file or reduce the image resolution.")
            elif "401" in error_message or "Authentication" in error_message:
                raise AuthenticationError("Authentication failed. Please check your API key.")
            elif "429" in error_message or "Rate limit" in error_message:
                raise RateLimitError("Rate limit exceeded. Please wait before retrying.")
            
            raise SVECTORError(f"Vision analysis failed: {error_message}")
    
    def analyze_from_url(
        self,
        image_url: str,
        prompt: Optional[str] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        detail: str = "auto",
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> VisionResponse:
        """
        Analyze an image from a URL
        
        Args:
            image_url: URL of the image
            prompt: Custom analysis prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            detail: Image detail level
            timeout: Request timeout
            max_retries: Maximum retries
            
        Returns:
            VisionResponse with analysis
        """
        return self.analyze(
            image_url=image_url,
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            detail=detail,
            timeout=timeout,
            max_retries=max_retries
        )
    
    def analyze_from_base64(
        self,
        base64_data: str,
        prompt: Optional[str] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        detail: str = "auto",
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> VisionResponse:
        """
        Analyze an image from base64 data
        
        Args:
            base64_data: Base64 encoded image
            prompt: Custom analysis prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            detail: Image detail level
            timeout: Request timeout
            max_retries: Maximum retries
            
        Returns:
            VisionResponse with analysis
        """
        return self.analyze(
            image_base64=base64_data,
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            detail=detail,
            timeout=timeout,
            max_retries=max_retries
        )
    
    def analyze_from_file_id(
        self,
        file_id: str,
        prompt: Optional[str] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        detail: str = "auto",
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None
    ) -> VisionResponse:
        """
        Analyze an uploaded file by file ID
        
        Args:
            file_id: File ID from files API
            prompt: Custom analysis prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            detail: Image detail level
            timeout: Request timeout
            max_retries: Maximum retries
            
        Returns:
            VisionResponse with analysis
        """
        return self.analyze(
            file_id=file_id,
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            detail=detail,
            timeout=timeout,
            max_retries=max_retries
        )
    
    def extract_text(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        file_id: Optional[str] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        **kwargs
    ) -> VisionResponse:
        """
        Extract text from an image (OCR functionality)
        
        Args:
            image_url: URL of the image
            image_base64: Base64 encoded image
            file_id: File ID from files API
            model: Model to use
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            VisionResponse with extracted text
        """
        return self.analyze(
            image_url=image_url,
            image_base64=image_base64,
            file_id=file_id,
            prompt="Extract and transcribe all text visible in this image. Return only the text content, maintaining the original formatting where possible.",
            model=model,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def describe_for_accessibility(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        file_id: Optional[str] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        **kwargs
    ) -> VisionResponse:
        """
        Describe image for accessibility purposes
        
        Args:
            image_url: URL of the image
            image_base64: Base64 encoded image
            file_id: File ID from files API
            model: Model to use
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            VisionResponse with accessibility description
        """
        return self.analyze(
            image_url=image_url,
            image_base64=image_base64,
            file_id=file_id,
            prompt="Provide a detailed description of this image suitable for screen readers and accessibility purposes. Include information about colors, layout, text, people, objects, and any other relevant visual elements.",
            model=model,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def detect_objects(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        file_id: Optional[str] = None,
        object_types: Optional[List[str]] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        **kwargs
    ) -> VisionResponse:
        """
        Detect specific objects in an image
        
        Args:
            image_url: URL of the image
            image_base64: Base64 encoded image
            file_id: File ID from files API
            object_types: List of object types to detect
            model: Model to use
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            VisionResponse with object detection results
        """
        if object_types:
            object_list = ", ".join(object_types)
        else:
            object_list = "people, vehicles, animals, furniture, electronics, and other significant objects"
        
        return self.analyze(
            image_url=image_url,
            image_base64=image_base64,
            file_id=file_id,
            prompt=f"Identify and list all instances of the following objects in this image: {object_list}. For each object, provide its location, size, and any relevant details.",
            model=model,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def compare_images(
        self,
        images: List[Dict[str, str]],
        prompt: Optional[str] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        detail: str = "auto",
        **kwargs
    ) -> VisionResponse:
        """
        Compare multiple images
        
        Args:
            images: List of image dicts with 'url', 'base64', or 'file_id' keys
            prompt: Custom comparison prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            detail: Image detail level
            **kwargs: Additional parameters
            
        Returns:
            VisionResponse with comparison results
        """
        message_content: List[Dict[str, Any]] = [
            {
                "type": "text",
                "text": prompt or "Compare these images and describe the similarities and differences."
            }
        ]
        
        # Add all images to the message content
        for image in images:
            if image.get("url"):
                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": image["url"],
                        "detail": detail
                    }
                })
            elif image.get("base64"):
                data_url = image["base64"] if image["base64"].startswith('data:') else f"data:image/jpeg;base64,{image['base64']}"
                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": data_url,
                        "detail": detail
                    }
                })
            elif image.get("file_id"):
                message_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": f"file://{image['file_id']}",
                        "detail": detail
                    }
                })
        
        chat_request = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": message_content
            }],
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        try:
            response = self._make_vision_request(chat_request)
            
            analysis = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not analysis:
                raise SVECTORError("No analysis content returned from API")
            
            return VisionResponse({
                "analysis": analysis,
                "usage": response.get("usage", {}),
                "_request_id": response.get("_request_id")
            })
            
        except Exception as e:
            raise SVECTORError(f"Image comparison failed: {e}")
    
    def analyze_with_confidence(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        file_id: Optional[str] = None,
        prompt: Optional[str] = None,
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        detail: str = "auto",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Analyze image with confidence scoring
        
        Args:
            image_url: URL of the image
            image_base64: Base64 encoded image
            file_id: File ID from files API
            prompt: Custom analysis prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            detail: Image detail level
            **kwargs: Additional parameters
            
        Returns:
            Dict with analysis and confidence score
        """
        enhanced_prompt = (prompt or "Analyze this image") + \
            " Please also provide a confidence score (0-100) for your analysis at the end in the format: [Confidence: XX%]"
        
        result = self.analyze(
            image_url=image_url,
            image_base64=image_base64,
            file_id=file_id,
            prompt=enhanced_prompt,
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            detail=detail,
            **kwargs
        )
        
        # Extract confidence score if present
        import re
        confidence_match = re.search(r'\[Confidence:\s*(\d+)%\]', result.analysis)
        confidence = int(confidence_match.group(1)) if confidence_match else None
        
        # Remove confidence notation from analysis
        clean_analysis = re.sub(r'\[Confidence:\s*\d+%\]', '', result.analysis).strip()
        
        return {
            "analysis": clean_analysis,
            "output_text": clean_analysis,
            "confidence": confidence,
            "usage": result.usage,
            "request_id": result.request_id
        }
    
    def batch_analyze(
        self,
        images: List[Dict[str, Any]],
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        detail: str = "auto",
        delay: float = 1.0,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        Batch analyze multiple images
        
        Args:
            images: List of image dicts with image data and optional prompt
            model: Model to use
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            detail: Image detail level
            delay: Delay between requests in seconds
            **kwargs: Additional parameters
            
        Returns:
            List of analysis results
        """
        results = []
        
        for i, image in enumerate(images):
            try:
                result = self.analyze(
                    image_url=image.get("image_url"),
                    image_base64=image.get("image_base64"),
                    file_id=image.get("file_id"),
                    prompt=image.get("prompt"),
                    model=model,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    detail=detail,
                    **kwargs
                )
                
                results.append({
                    "analysis": result.analysis,
                    "output_text": result.analysis,
                    "usage": result.usage,
                    "request_id": result.request_id
                })
                
                # Add delay between requests
                if i < len(images) - 1:
                    time.sleep(delay)
                    
            except Exception as e:
                results.append({
                    "analysis": "",
                    "output_text": "",
                    "error": str(e)
                })
        
        return results
        
    def generate_caption(
        self,
        image_url: Optional[str] = None,
        image_base64: Optional[str] = None,
        file_id: Optional[str] = None,
        style: str = "casual",
        model: str = "spec-3-turbo",
        max_tokens: int = 1000,
        **kwargs
    ) -> VisionResponse:
        """
        Generate image captions optimized for social media
        
        Args:
            image_url: URL of the image
            image_base64: Base64 encoded image
            file_id: File ID from files API
            style: Caption style ('professional', 'casual', 'funny', 'technical')
            model: Model to use
            max_tokens: Maximum tokens
            **kwargs: Additional parameters
            
        Returns:
            VisionResponse with generated caption
        """
        style_prompts = {
            "professional": "Generate a professional, informative caption for this image suitable for business or educational content.",
            "casual": "Write a casual, friendly caption for this image that would work well on social media.",
            "funny": "Create a humorous, entertaining caption for this image that would get engagement on social media.",
            "technical": "Provide a detailed, technical description of this image suitable for academic or scientific purposes."
        }
        
        prompt = style_prompts.get(style, style_prompts["casual"])
        
        return self.analyze(
            image_url=image_url,
            image_base64=image_base64,
            file_id=file_id,
            prompt=prompt,
            model=model,
            max_tokens=max_tokens,
            **kwargs
        )
    
    def create_response(
        self,
        model: str,
        input: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> VisionResponse:
        """
        Create a vision response using the advanced input format
        
        This method provides compatibility with the Node.js/JSR SDK format
        and allows for complex multi-modal inputs.
        
        Args:
            model: Model to use
            input: List of input messages with role and content
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            VisionResponse with output_text
            
        Example:
            response = client.vision.create_response(
                model="spec-3-turbo",
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "what's in this image?"},
                        {"type": "input_image", "image_url": "https://example.com/image.jpg"}
                    ]
                }]
            )
            print(response.output_text)
        """
        # Find the user message
        user_message = None
        for msg in input:
            if msg.get("role") == "user":
                user_message = msg
                break
        
        if not user_message:
            raise ValueError("User message is required")
        
        prompt = ""
        image_url = None
        image_base64 = None
        file_id = None
        
        # Parse the content
        for content in user_message.get("content", []):
            if content.get("type") == "input_text":
                prompt += content.get("text", "") + " "
            elif content.get("type") == "input_image":
                if content.get("image_url"):
                    if content["image_url"].startswith("data:"):
                        image_base64 = content["image_url"]
                    else:
                        image_url = content["image_url"]
                elif content.get("file_id"):
                    file_id = content["file_id"]
        
        # Use the vision API
        return self.analyze(
            image_url=image_url,
            image_base64=image_base64,
            file_id=file_id,
            prompt=prompt.strip(),
            model=model,
            max_tokens=max_tokens or 1000,
            temperature=temperature or 0.7,
            **kwargs
        )


class ResponsesAPI:
    """
    Responses API for SVECTOR Vision
    
    Provides a simplified interface matching the examples in the request.
    This is an alias/wrapper around the Vision API for better compatibility.
    """
    
    def __init__(self, client):
        self.client = client
        
    def create(
        self,
        model: str,
        input: List[Dict[str, Any]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        **kwargs
    ) -> VisionResponse:
        """
        Create a vision response using the input format
        
        Args:
            model: Model to use
            input: List of input messages with role and content
            max_tokens: Maximum tokens
            temperature: Sampling temperature
            **kwargs: Additional parameters
            
        Returns:
            VisionResponse with output_text
            
        Example:
            response = client.responses.create(
                model="spec-3-turbo",
                input=[{
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "what's in this image?"},
                        {"type": "input_image", "image_url": "https://example.com/image.jpg"}
                    ]
                }]
            )
            print(response.output_text)
        """
        # Find the user message
        user_message = None
        for msg in input:
            if msg.get("role") == "user":
                user_message = msg
                break
        
        if not user_message:
            raise ValueError("User message is required")
        
        prompt = ""
        image_url = None
        image_base64 = None
        file_id = None
        
        # Parse the content
        for content in user_message.get("content", []):
            if content.get("type") == "input_text":
                prompt += content.get("text", "") + " "
            elif content.get("type") == "input_image":
                if content.get("image_url"):
                    if content["image_url"].startswith("data:"):
                        image_base64 = content["image_url"]
                    else:
                        image_url = content["image_url"]
                elif content.get("file_id"):
                    file_id = content["file_id"]
        
        # Use the vision API
        return self.client.vision.analyze(
            image_url=image_url,
            image_base64=image_base64,
            file_id=file_id,
            prompt=prompt.strip(),
            model=model,
            max_tokens=max_tokens or 1000,
            temperature=temperature or 0.7,
            **kwargs
        )


# Utility functions
def encode_image(image_path: Union[str, Path]) -> str:
    """
    Encode an image file to base64 string
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Base64 encoded string
        
    Example:
        base64_image = encode_image("path/to/image.jpg")
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def create_data_url(base64_data: str, mime_type: str = "image/jpeg") -> str:
    """
    Create a data URL from base64 data
    
    Args:
        base64_data: Base64 encoded image data
        mime_type: MIME type of the image
        
    Returns:
        Data URL string
        
    Example:
        data_url = create_data_url(base64_data, "image/png")
    """
    return f"data:{mime_type};base64,{base64_data}"
