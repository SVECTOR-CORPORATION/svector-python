"""
SVECTOR Conversations API

conversation interface with instructions and input.
Handles system role conversion internally for a clean user experience.
"""

import json
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union


class ConversationRequest:
    """Request structure for conversations API"""
    def __init__(
        self,
        model: str,
        instructions: Optional[str] = None,
        input: str = "",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False,
        files: Optional[List[Dict[str, str]]] = None,
        context: Optional[List[str]] = None,
    ):
        self.model = model
        self.instructions = instructions
        self.input = input
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.stream = stream
        self.files = files or []
        self.context = context or []


class ConversationResponse:
    """Response structure for conversations API"""
    def __init__(self, data: Dict[str, Any]):
        self.output = data.get("output", "")
        self.usage = data.get("usage", {})
        self.request_id = data.get("_request_id")
        self._raw_data = data

    def __str__(self):
        return self.output


class ConversationStreamEvent:
    """Stream event for conversations API"""
    def __init__(self, data: Dict[str, Any]):
        self.content = data.get("content", "")
        self.done = data.get("done", False)
        self._raw_data = data

    def __str__(self):
        return self.content


class ConversationsAPI:
    """
    Conversations API
    
    Provides a clean interface for AI conversations using instructions and input,
    automatically handling system role conversion internally.
    """
    
    def __init__(self, client):
        self.client = client
        
    def create(
        self,
        model: str,
        instructions: Optional[str] = None,
        input: str = "",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        files: Optional[List[Dict[str, str]]] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> ConversationResponse:
        """
        Create a conversation with instructions and input.
        
        Args:
            model: The model to use (e.g., 'spec-3-turbo')
            instructions: System instructions for the model
            input: User input/question
            max_tokens: Maximum tokens to generate
            temperature: Randomness (0.0 to 2.0)
            files: List of file references for RAG
            context: Previous conversation context
            **kwargs: Additional parameters
            
        Returns:
            ConversationResponse with output and metadata
            
        Example:
            response = client.conversations.create(
                model="spec-3-turbo",
                instructions="You are a helpful assistant.",
                input="What is machine learning?",
                temperature=0.7
            )
            print(response.output)
        """
        # Convert interface to internal chat format
        messages = self._build_messages(instructions, input, context)
        
        # Prepare chat request
        chat_data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "files": files or [],
            **kwargs
        }
        
        # Remove None values
        chat_data = {k: v for k, v in chat_data.items() if v is not None}
        
        # Make request using internal chat API
        response = self.client.chat.create(**chat_data)
        
        # Convert to format
        output = ""
        if response.get("choices") and len(response["choices"]) > 0:
            output = response["choices"][0]["message"]["content"]
            
        return ConversationResponse({
            "output": output,
            "usage": response.get("usage", {}),
            "_request_id": response.get("_request_id")
        })
    
    def create_stream(
        self,
        model: str,
        instructions: Optional[str] = None,
        input: str = "",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        files: Optional[List[Dict[str, str]]] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> Iterator[ConversationStreamEvent]:
        """
        Create a streaming conversation.
        
        Args:
            model: The model to use
            instructions: System instructions
            input: User input
            max_tokens: Maximum tokens
            temperature: Randomness
            files: File references
            context: Previous context
            **kwargs: Additional parameters
            
        Yields:
            ConversationStreamEvent objects with content and done status
            
        Example:
            stream = client.conversations.create_stream(
                model="spec-3-turbo",
                instructions="You are a storyteller.",
                input="Tell me a short story.",
                stream=True
            )
            
            for event in stream:
                if not event.done:
                    print(event.content, end="", flush=True)
        """
        # Convert to internal format
        messages = self._build_messages(instructions, input, context)
        
        chat_data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "files": files or [],
            # Don't pass stream=True here, let create_stream handle it
        }
        
        # Remove None values and 'stream' to avoid conflicts
        chat_data = {k: v for k, v in chat_data.items() if v is not None and k != 'stream'}
        
        # Add any additional kwargs except 'stream'
        for k, v in kwargs.items():
            if k != 'stream':
                chat_data[k] = v
        
        # Stream using internal chat API
        for event in self.client.chat.create_stream(**chat_data):
            # Transform internal events to format
            content = ""
            done = False
            
            if "choices" in event and len(event["choices"]) > 0:
                delta = event["choices"][0].get("delta", {})
                content = delta.get("content", "")
                finish_reason = event["choices"][0].get("finish_reason")
                if finish_reason:
                    done = True
                    
            yield ConversationStreamEvent({
                "content": content,
                "done": done
            })
    
    def create_with_response(
        self,
        model: str,
        instructions: Optional[str] = None,
        input: str = "",
        **kwargs
    ) -> tuple[ConversationResponse, Any]:
        """
        Create conversation and return both data and raw response.
        
        Returns:
            Tuple of (ConversationResponse, raw_response)
        """
        messages = self._build_messages(instructions, input, kwargs.get("context", []))
        
        chat_data = {
            "model": model,
            "messages": messages,
            **{k: v for k, v in kwargs.items() if k != "context"}
        }
        
        response, raw = self.client.chat.create_with_response(**chat_data)
        
        output = ""
        if response.get("choices") and len(response["choices"]) > 0:
            output = response["choices"][0]["message"]["content"]
            
        conversation_response = ConversationResponse({
            "output": output,
            "usage": response.get("usage", {}),
            "_request_id": response.get("_request_id")
        })
        
        return conversation_response, raw
    
    def _build_messages(
        self, 
        instructions: Optional[str], 
        input: str, 
        context: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """
        Build messages array from conversation parameters.
        
        Converts instructions + input + context to proper role-based messages.
        """
        messages = []
        
        # Add system instructions if provided
        if instructions:
            messages.append({
                "role": "system",
                "content": instructions
            })
        
        # Add context messages if provided (alternating user/assistant)
        if context:
            for i, msg in enumerate(context):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({
                    "role": role,
                    "content": msg
                })
        
        # Add current user input
        messages.append({
            "role": "user",
            "content": input
        })
        
        return messages


class AsyncConversationsAPI:
    """Async version of ConversationsAPI"""
    
    def __init__(self, client):
        self.client = client
        
    async def create(
        self,
        model: str,
        instructions: Optional[str] = None,
        input: str = "",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        files: Optional[List[Dict[str, str]]] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> ConversationResponse:
        """Async version of create"""
        messages = self._build_messages(instructions, input, context)
        
        chat_data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "files": files or [],
            **kwargs
        }
        
        chat_data = {k: v for k, v in chat_data.items() if v is not None}
        response = await self.client.chat.create(**chat_data)
        
        output = ""
        if response.get("choices") and len(response["choices"]) > 0:
            output = response["choices"][0]["message"]["content"]
            
        return ConversationResponse({
            "output": output,
            "usage": response.get("usage", {}),
            "_request_id": response.get("_request_id")
        })
    
    async def create_stream(
        self,
        model: str,
        instructions: Optional[str] = None,
        input: str = "",
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        files: Optional[List[Dict[str, str]]] = None,
        context: Optional[List[str]] = None,
        **kwargs
    ) -> AsyncIterator[ConversationStreamEvent]:
        """Async version of create_stream"""
        messages = self._build_messages(instructions, input, context)
        
        chat_data = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "files": files or [],
            # Don't pass stream=True here, let create_stream handle it
        }
        
        # Remove None values and 'stream' to avoid conflicts
        chat_data = {k: v for k, v in chat_data.items() if v is not None and k != 'stream'}
        
        # Add any additional kwargs except 'stream'
        for k, v in kwargs.items():
            if k != 'stream':
                chat_data[k] = v
        
        async for event in self.client.chat.create_stream(**chat_data):
            content = ""
            done = False
            
            if "choices" in event and len(event["choices"]) > 0:
                delta = event["choices"][0].get("delta", {})
                content = delta.get("content", "")
                finish_reason = event["choices"][0].get("finish_reason")
                if finish_reason:
                    done = True
                    
            yield ConversationStreamEvent({
                "content": content,
                "done": done
            })
    
    def _build_messages(
        self, 
        instructions: Optional[str], 
        input: str, 
        context: Optional[List[str]] = None
    ) -> List[Dict[str, str]]:
        """Same as sync version"""
        messages = []
        
        if instructions:
            messages.append({
                "role": "system",
                "content": instructions
            })
        
        if context:
            for i, msg in enumerate(context):
                role = "user" if i % 2 == 0 else "assistant"
                messages.append({
                    "role": role,
                    "content": msg
                })
        
        messages.append({
            "role": "user",
            "content": input
        })
        
        return messages
