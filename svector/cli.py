#!/usr/bin/env python3

"""
SVECTOR CLI - Command Line Interface for SVECTOR AI
"""

import argparse
import json
import os
import sys
from pathlib import Path

from svector import SVECTOR

CONFIG_DIR = Path.home() / '.svector'
CONFIG_FILE = CONFIG_DIR / 'config.json'

def ensure_config_dir():
    """Ensure config directory exists"""
    CONFIG_DIR.mkdir(exist_ok=True)

def load_config():
    """Load configuration from file"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return {}

def save_config(config):
    """Save configuration to file"""
    try:
        ensure_config_dir()
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_client():
    """Get SVECTOR client with API key"""
    config = load_config()
    api_key = os.getenv('SVECTOR_API_KEY') or config.get('api_key')
    
    if not api_key:
        print("No API key found.")
        print("Set it with: svector config set-key <your-api-key>")
        print("Or set SVECTOR_API_KEY environment variable")
        sys.exit(1)
        
    return SVECTOR(api_key=api_key)

def cmd_chat(args):
    """Handle chat command"""
    client = get_client()
    
    try:
        response = client.chat.create(
            model=args.model,
            messages=[{"role": "user", "content": args.message}],
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            files=[{"type": "file", "id": args.file}] if args.file else None
        )
        
        print("SVECTOR AI:")
        print(response["choices"][0]["message"]["content"])
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def cmd_stream(args):
    """Handle stream command"""
    client = get_client()
    
    try:
        print(" SVECTOR AI (streaming):")
        
        stream = client.chat.create(
            model=args.model,
            messages=[{"role": "user", "content": args.message}],
            temperature=args.temperature,
            stream=True
        )
        
        for event in stream:
            if event.get("choices") and event["choices"][0].get("delta", {}).get("content"):
                print(event["choices"][0]["delta"]["content"], end="", flush=True)
        print()  # New line at the end
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def cmd_models(args):
    """Handle models command"""
    client = get_client()
    
    try:
        models = client.models.list()
        print("📋 Available models:")
        for i, model in enumerate(models["models"], 1):
            print(f"  {i}. {model}")
            
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def cmd_config(args):
    """Handle config command"""
    config = load_config()
    
    if args.config_action == "set-key":
        if not args.api_key:
            print("Usage: svector config set-key <api-key>")
            sys.exit(1)
        config["api_key"] = args.api_key
        save_config(config)
        print("API key saved successfully")
        
    elif args.config_action == "show":
        print("Current configuration:")
        print(json.dumps(config, indent=2))
        
    else:
        print("Usage: svector config [set-key|show]")
        sys.exit(1)

def cmd_file(args):
    """Handle file command"""
    client = get_client()
    
    if args.file_action == "upload":
        if not args.filepath:
            print("Usage: svector file upload <filepath>")
            sys.exit(1)
            
        if not os.path.exists(args.filepath):
            print(f"File not found: {args.filepath}")
            sys.exit(1)
            
        try:
            print(f" Uploading {args.filepath}...")
            response = client.files.create(args.filepath, purpose="default")
            print(f"File uploaded with ID: {response['file_id']}")
            
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    else:
        print("Usage: svector file upload <filepath>")
        sys.exit(1)

def cmd_ask(args):
    """Handle ask command"""
    client = get_client()
    
    if not args.file:
        print("Please specify a file ID with --file <file-id>")
        sys.exit(1)
        
    try:
        response = client.chat.create(
            model="spec-3-turbo",
            messages=[{"role": "user", "content": args.question}],
            files=[{"type": "file", "id": args.file}]
        )
        
        print("SVECTOR AI (with file):")
        print(response["choices"][0]["message"]["content"])
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="SVECTOR CLI - Advanced AI with RAG capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  svector chat "What is artificial intelligence?"
  svector stream "Write a poem about technology"
  svector models
  svector config set-key sk-your-api-key-here
  svector file upload document.pdf
  svector ask "Summarize this document" --file file-123

For more info: https://www.svector.co.in
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Chat command
    chat_parser = subparsers.add_parser("chat", help="Send a chat message")
    chat_parser.add_argument("message", help="Message to send")
    chat_parser.add_argument("--model", default="spec-3-turbo", help="Model to use")
    chat_parser.add_argument("--temperature", type=float, default=0.7, help="Temperature (0.0-2.0)")
    chat_parser.add_argument("--max-tokens", type=int, default=150, help="Max tokens")
    chat_parser.add_argument("--file", help="File ID for RAG")
    chat_parser.set_defaults(func=cmd_chat)
    
    # Stream command
    stream_parser = subparsers.add_parser("stream", help="Stream a chat response")
    stream_parser.add_argument("message", help="Message to send")
    stream_parser.add_argument("--model", default="spec-3-turbo", help="Model to use")
    stream_parser.add_argument("--temperature", type=float, default=0.7, help="Temperature (0.0-2.0)")
    stream_parser.set_defaults(func=cmd_stream)
    
    # Models command
    models_parser = subparsers.add_parser("models", help="List available models")
    models_parser.set_defaults(func=cmd_models)
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_subparsers = config_parser.add_subparsers(dest="config_action")
    
    setkey_parser = config_subparsers.add_parser("set-key", help="Set API key")
    setkey_parser.add_argument("api_key", help="Your SVECTOR API key")
    
    show_parser = config_subparsers.add_parser("show", help="Show current config")
    config_parser.set_defaults(func=cmd_config)
    
    # File command
    file_parser = subparsers.add_parser("file", help="File operations")
    file_subparsers = file_parser.add_subparsers(dest="file_action")
    
    upload_parser = file_subparsers.add_parser("upload", help="Upload a file")
    upload_parser.add_argument("filepath", help="Path to file to upload")
    file_parser.set_defaults(func=cmd_file)
    
    # Ask command
    ask_parser = subparsers.add_parser("ask", help="Ask a question about a file")
    ask_parser.add_argument("question", help="Question to ask")
    ask_parser.add_argument("--file", required=True, help="File ID to query")
    ask_parser.set_defaults(func=cmd_ask)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
        
    args.func(args)

if __name__ == "__main__":
    main()
