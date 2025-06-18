#!/usr/bin/env python3

"""
SVECTOR Python SDK Examples
"""

import os

from svector import SVECTOR

# Set up the client
api_key = os.getenv('SVECTOR_API_KEY', 'sk-your-api-key-here')
client = SVECTOR(api_key=api_key)

def example_basic_chat():
    """Basic chat example"""
    print("Basic Chat Example")
    print("-" * 50)
    
    try:
        response = client.chat.create(
            model="spec-3-turbo:latest",
            messages=[
                {"role": "user", "content": "What is artificial intelligence?"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        print("Question: What is artificial intelligence?")
        print("Answer:", response["choices"][0]["message"]["content"])
        print("Usage:", response.get("usage", "N/A"))
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def example_streaming():
    """Streaming example"""
    print(" Streaming Example")
    print("-" * 50)
    
    try:
        print("Question: Write a haiku about Python programming")
        print("Streaming Answer: ", end="", flush=True)
        
        stream = client.chat.create(
            model="spec-3-turbo:latest",
            messages=[
                {"role": "user", "content": "Write a haiku about Python programming"}
            ],
            temperature=0.8,
            stream=True
        )
        
        for event in stream:
            if event.get("choices") and event["choices"][0].get("delta", {}).get("content"):
                print(event["choices"][0]["delta"]["content"], end="", flush=True)
        
        print("\nStreaming completed!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def example_models():
    """Models listing example"""
    print("📋 Models Example")
    print("-" * 50)
    
    try:
        models = client.models.list()
        print(f"Available models ({len(models['models'])}):")
        for i, model in enumerate(models["models"], 1):
            print(f"  {i}. {model}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def example_conversation():
    """Multi-turn conversation example"""
    print("  Multi-turn Conversation Example")
    print("-" * 50)
    
    conversation = [
        {"role": "system", "content": "You are a helpful Python programming assistant."}
    ]
    
    questions = [
        "How do I create a list in Python?",
        "Can you show me an example?",
        "How do I add items to the list?"
    ]
    
    try:
        for i, question in enumerate(questions, 1):
            print(f"👤 Question {i}: {question}")
            
            conversation.append({"role": "user", "content": question})
            
            response = client.chat.create(
                model="spec-3-turbo:latest",
                messages=conversation,
                temperature=0.3,
                max_tokens=100
            )
            
            answer = response["choices"][0]["message"]["content"]
            conversation.append({"role": "assistant", "content": answer})
            
            print(f"Answer {i}: {answer}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
    
    print()

def example_error_handling():
    """Error handling example"""
    print(" Error Handling Example")
    print("-" * 50)
    
    # Test with invalid API key
    try:
        invalid_client = SVECTOR(api_key="invalid-key")
        response = invalid_client.chat.create(
            model="spec-3-turbo:latest",
            messages=[{"role": "user", "content": "This should fail"}]
        )
        print("Should have failed with invalid API key")
        
    except Exception as e:
        print("Successfully caught authentication error:")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Message: {e}")
    
    print()

def main():
    """Run all examples"""
    print("SVECTOR Python SDK Examples")
    print("=" * 60)
    print()
    
    examples = [
        example_basic_chat,
        example_streaming,
        example_models,
        example_conversation,
        example_error_handling
    ]
    
    for example in examples:
        try:
            example()
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
            break
        except Exception as e:
            print(f"Example failed: {e}")
            print()
    
    print("🎉 Examples completed!")

if __name__ == "__main__":
    main()
