"""
SVECTOR Python SDK - Comprehensive Examples

This file demonstrates the Conversations API and advanced features.
"""

import asyncio
import os
from pathlib import Path

# Import the SVECTOR clients
from svector import SVECTOR, AsyncSVECTOR


def basic_conversation_example():
    """Basic conversation using the API"""
    print("SVECTOR Python SDK - Conversations API")
    print("=" * 60)
    
    # Initialize client
    client = SVECTOR(api_key=os.environ.get("SVECTOR_API_KEY"))
    
    # Simple conversation with instructions
    print("\n Basic Conversation")
    print("-" * 30)
    
    response = client.conversations.create(
        model="spec-3-turbo:latest",
        instructions="You are a helpful AI assistant that explains complex topics clearly.",
        input="What is machine learning?",
        temperature=0.7,
        max_tokens=200
    )
    
    print(f"Question: What is machine learning?")
    print(f"Answer: {response.output}")
    print(f"Request ID: {response.request_id}")
    print(f"Token Usage: {response.usage}")


def conversation_with_context_example():
    """Conversation with context history"""
    print("\n Conversation with Context")
    print("-" * 30)
    
    client = SVECTOR()
    
    response = client.conversations.create(
        model="spec-3-turbo:latest",
        instructions="You are a programming tutor that helps students learn coding.",
        input="Can you show me an example?",
        context=[
            "How do I create a function in Python?",
            "You can create a function using the def keyword followed by the function name and parameters in parentheses, then a colon and the function body indented."
        ],
        temperature=0.5
    )
    
    print("Context: Previous conversation about Python functions")
    print(f"Follow-up Question: Can you show me an example?")
    print(f"Answer: {response.output}")


def streaming_conversation_example():
    """Streaming conversation example"""
    print("\n Streaming Conversation")
    print("-" * 30)
    
    client = SVECTOR()
    
    print("Question: Tell me a short story about robots and humans.")
    print("Streaming Answer: ", end="", flush=True)
    
    stream = client.conversations.create_stream(
        model="spec-3-turbo:latest",
        instructions="You are a creative storyteller who writes engaging short stories.",
        input="Tell me a short story about robots and humans working together.",
        stream=True
    )
    
    for event in stream:
        if not event.done:
            print(event.content, end="", flush=True)
        else:
            print("\n✓ Story completed!")
            break


def document_processing_example():
    """Document processing and Q&A example"""
    print("\n Document Processing & Q&A")
    print("-" * 30)
    
    client = SVECTOR()
    
    # Create a sample document
    sample_content = """
    # SVECTOR AI Research Report
    
    ## Executive Summary
    SVECTOR has developed cutting-edge foundational AI models including:
    - Spec-3: Advanced reasoning model
    - Spec-3-Turbo: Fast, efficient model for most use cases
    - Theta-35: Complex mathematical reasoning
    - Theta-35-Mini: Lightweight model for simple tasks
    
    ## Key Findings
    1. Performance improvements of 40% over previous generation
    2. Reduced inference time by 60%
    3. Enhanced mathematical reasoning capabilities
    4. Better code generation and understanding
    
    ## Applications
    - Conversational AI assistants
    - Code generation and review
    - Mathematical problem solving
    - Document analysis and summarization
    """
    
    try:
        # Upload the document
        print("📤 Uploading document...")
        file_response = client.files.create(
            file=sample_content.encode(),
            purpose="default",
            filename="svector_research_report.md"
        )
        
        print(f"Document uploaded successfully! File ID: {file_response['file_id']}")
        
        # Ask questions about the document
        print("\n🔍 Asking questions about the document...")
        
        response = client.conversations.create(
            model="spec-3-turbo:latest",
            instructions="You are a research assistant that analyzes documents and answers questions based on their content. Cite specific information from the documents when possible.",
            input="What are the key performance improvements mentioned in the report?",
            files=[{"type": "file", "id": file_response["file_id"]}],
            temperature=0.3  # Lower temperature for more factual responses
        )
        
        print(f"Question: What are the key performance improvements mentioned in the report?")
        print(f"Answer: {response.output}")
        
    except Exception as e:
        print(f"Document processing failed: {e}")


def model_comparison_example():
    """Compare different SVECTOR models"""
    print("\n🔬 Model Comparison")
    print("-" * 30)
    
    client = SVECTOR()
    
    models = ["spec-3-turbo:latest", "theta-35-mini:latest"]
    prompt = "Explain quantum computing in simple terms."
    
    print(f"Comparing models for: '{prompt}'\n")
    
    for model in models:
        try:
            print(f"Model: {model}")
            response = client.conversations.create(
                model=model,
                instructions="You are a physics teacher who explains complex topics simply.",
                input=prompt,
                max_tokens=100,
                temperature=0.7
            )
            print(f"Response: {response.output}")
            print(f"Tokens used: {response.usage.get('total_tokens', 'N/A')}")
            print()
        except Exception as e:
            print(f"Failed for {model}: {e}\n")


def advanced_chat_api_example():
    """Advanced Chat API with role-based messages"""
    print("\n Advanced Chat API (Role-based)")
    print("-" * 30)
    
    client = SVECTOR()
    
    # Multi-turn conversation with explicit roles
    messages = [
        {"role": "system", "content": "You are a helpful programming assistant with expertise in Python."},
        {"role": "user", "content": "How do I handle exceptions in Python?"},
        {"role": "assistant", "content": "You can handle exceptions in Python using try-except blocks. Here's the basic syntax:\n\ntry:\n    # code that might raise an exception\nexcept ExceptionType:\n    # handle the exception"},
        {"role": "user", "content": "Can you show me a more specific example with file operations?"}
    ]
    
    response = client.chat.create(
        model="spec-3-turbo:latest",
        messages=messages,
        temperature=0.5
    )
    
    print("Multi-turn conversation with explicit roles:")
    print(f"Final Response: {response['choices'][0]['message']['content']}")


def error_handling_example():
    """Demonstrate comprehensive error handling"""
    print("\n Error Handling")
    print("-" * 30)
    
    from svector import APIError, AuthenticationError, RateLimitError

    # Test with invalid API key
    try:
        client = SVECTOR(api_key="invalid-key")
        response = client.conversations.create(
            model="spec-3-turbo:latest",
            instructions="You are helpful.",
            input="Hello"
        )
    except AuthenticationError as e:
        print(f"Caught authentication error: {e}")
    except RateLimitError as e:
        print(f"⏰ Rate limit exceeded: {e}")
    except APIError as e:
        print(f"🚨 API error: {e}")
    except Exception as e:
        print(f"💥 Unexpected error: {e}")


async def async_conversation_example():
    """Async conversation example"""
    print("\n⚡ Async Conversation")
    print("-" * 30)
    
    async with AsyncSVECTOR(api_key=os.environ.get("SVECTOR_API_KEY")) as client:
        # Multiple async conversations
        tasks = [
            client.conversations.create(
                model="spec-3-turbo:latest",
                instructions="You are a helpful assistant.",
                input=f"What is {topic}?"
            )
            for topic in ["artificial intelligence", "quantum computing", "blockchain"]
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        topics = ["artificial intelligence", "quantum computing", "blockchain"]
        for topic, response in zip(topics, responses):
            if isinstance(response, Exception):
                print(f"{topic}: Error - {response}")
            else:
                print(f"{topic}: {response.output[:100]}...")


async def async_streaming_example():
    """Async streaming example"""
    print("\n Async Streaming")
    print("-" * 30)
    
    async with AsyncSVECTOR() as client:
        print("Question: Write a haiku about technology.")
        print("Streaming Response: ", end="", flush=True)
        
        stream = client.conversations.create_stream(
            model="spec-3-turbo:latest",
            instructions="You are a creative poet.",
            input="Write a haiku about technology.",
            stream=True
        )
        
        async for event in stream:
            if not event.done:
                print(event.content, end="", flush=True)
            else:
                print("\n✓ Haiku completed!")
                break


def intelligent_chat_class_example():
    """Example of building an intelligent chat class"""
    print("\nIntelligent Chat Class")
    print("-" * 30)
    
    class IntelligentChat:
        def __init__(self, api_key: str):
            self.client = SVECTOR(api_key=api_key)
            self.conversation_history = []
        
        def chat(self, user_message: str, system_instructions: str = None) -> str:
            # Add user message to history
            self.conversation_history.append(user_message)
            
            response = self.client.conversations.create(
                model="spec-3-turbo:latest",
                instructions=system_instructions or "You are a helpful and friendly AI assistant.",
                input=user_message,
                context=self.conversation_history[-10:],  # Keep last 10 messages
                temperature=0.7
            )
            
            # Add AI response to history
            self.conversation_history.append(response.output)
            return response.output
        
        def clear_history(self):
            self.conversation_history = []
    
    # Usage
    chat = IntelligentChat(os.environ.get("SVECTOR_API_KEY"))
    
    print("Chat 1:", chat.chat("Hello! How are you?"))
    print("Chat 2:", chat.chat("What did I just ask you?"))
    
    # Specialized chat
    physics_response = chat.chat(
        "Explain relativity", 
        "You are a physics professor who explains complex topics in simple terms."
    )
    print("Physics Chat:", physics_response[:100] + "...")


def document_analyzer_example():
    """Advanced document analyzer class"""
    print("\n Document Analyzer")
    print("-" * 30)
    
    class DocumentAnalyzer:
        def __init__(self):
            self.client = SVECTOR()
            self.uploaded_files = []
        
        def add_document(self, content: str, filename: str) -> str:
            try:
                file_response = self.client.files.create(
                    file=content.encode(),
                    purpose="default",
                    filename=filename
                )
                file_id = file_response["file_id"]
                self.uploaded_files.append(file_id)
                return file_id
            except Exception as e:
                print(f"Failed to upload {filename}: {e}")
                return None
        
        def analyze(self, query: str, analysis_type: str = "insights") -> str:
            instructions = {
                "summary": "You are an expert document summarizer. Provide clear, concise summaries.",
                "insights": "You are a research analyst. Extract key insights, patterns, and important findings.",
                "questions": "You are an expert analyst. Answer questions based on the provided documents."
            }
            
            response = self.client.conversations.create(
                model="spec-3-turbo:latest",
                instructions=instructions.get(analysis_type, instructions["insights"]),
                input=query,
                files=[{"type": "file", "id": file_id} for file_id in self.uploaded_files],
                temperature=0.3
            )
            
            return response.output
    
    # Usage
    analyzer = DocumentAnalyzer()
    
    # Add sample documents
    doc1_content = """
    # Q1 Financial Report
    Revenue: $2.5M (up 25% from Q4)
    Expenses: $1.8M
    Net Income: $700K
    Key achievements: Launched new product line, expanded team by 30%
    """
    
    doc2_content = """
    # Q1 Marketing Report
    Website traffic: 150K visitors (up 40%)
    Conversion rate: 3.2%
    Social media growth: 25% increase in followers
    Campaign performance: Email campaigns showed 18% open rates
    """
    
    file1 = analyzer.add_document(doc1_content, "q1_financial.md")
    file2 = analyzer.add_document(doc2_content, "q1_marketing.md")
    
    if file1 and file2:
        # Analyze the documents
        summary = analyzer.analyze("Provide a comprehensive summary of Q1 performance", "summary")
        print(f"Summary: {summary}")
        
        insights = analyzer.analyze("What are the key business trends and growth indicators?", "insights")
        print(f"Insights: {insights[:200]}...")


def main():
    """Run all examples"""
    print("SVECTOR Python SDK - Comprehensive Examples")
    print("=" * 60)
    
    # Check if API key is available
    if not os.environ.get("SVECTOR_API_KEY"):
        print("⚠️  Warning: SVECTOR_API_KEY environment variable not set.")
        print("Some examples may fail. Get your API key from https://www.svector.co.in")
        print()
    
    try:
        # Sync examples
        basic_conversation_example()
        conversation_with_context_example()
        streaming_conversation_example()
        document_processing_example()
        model_comparison_example()
        advanced_chat_api_example()
        error_handling_example()
        intelligent_chat_class_example()
        document_analyzer_example()
        
        # Async examples
        print("\n" + "=" * 60)
        print("Async Examples")
        print("=" * 60)
        
        # Run async examples
        asyncio.run(async_conversation_example())
        asyncio.run(async_streaming_example())
        
        print("\n✨ All examples completed successfully!")
        
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\nExample failed: {e}")


if __name__ == "__main__":
    main()
