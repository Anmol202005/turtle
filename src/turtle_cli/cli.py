#!/usr/bin/env python3
"""
Main CLI entry point for Turtle CLI.
Multi-API AI coding assistant.
"""

import argparse
import os
import sys
import logging
from pathlib import Path
from typing import Optional

from .llm.client import LLMClient
from .llm.conversation import ConversationManager
from .tools.protocol import ToolRegistry
from .tools.adapters import (
    ReadFileTool, WriteFileTool, ListDirectoryTool, ExecuteCommandTool
)
from .tools.loop import ToolOrchestrator
from .tools.streaming import StreamingToolOrchestrator
from .setup.wizard import run_first_time_setup, run_forced_setup


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def load_config() -> dict:
    """Load configuration from environment variables and config files."""
    config = {}

    # Try to load from .env file
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value

    # Get values from environment
    config['provider'] = os.getenv('TURTLE_PROVIDER')
    config['model'] = os.getenv('TURTLE_MODEL')
    config['api_key'] = os.getenv('TURTLE_API_KEY')

    return config


def validate_config(config: dict) -> bool:
    """Validate that all required configuration is present."""
    required_fields = ['provider', 'model', 'api_key']
    for field in required_fields:
        if not config.get(field):
            return False
    return True


def initialize_tools() -> ToolRegistry:
    """Initialize and register all available tools."""
    registry = ToolRegistry()

    # Register filesystem and command tools
    registry.register(ReadFileTool())
    registry.register(WriteFileTool())
    registry.register(ListDirectoryTool())
    registry.register(ExecuteCommandTool())

    return registry


def interactive_mode(llm_client: LLMClient, conversation_manager: ConversationManager,
                   tool_registry: ToolRegistry, streaming: bool = False):
    """Run the CLI in interactive mode."""
    print("🐢 Turtle CLI - Interactive Mode")
    print("Type 'exit' to quit, 'reset' to clear conversation")
    print("=" * 50)

    if streaming:
        orchestrator = StreamingToolOrchestrator(
            llm_client=llm_client,
            conversation_manager=conversation_manager,
            tool_registry=tool_registry
        )
    else:
        orchestrator = ToolOrchestrator(
            llm_client=llm_client,
            conversation_manager=conversation_manager,
            tool_registry=tool_registry
        )

    try:
        while True:
            user_input = input("\n> ").strip()

            if user_input.lower() in ['exit', 'quit']:
                break
            elif user_input.lower() == 'reset':
                conversation_manager.reset_conversation(keep_system_prompt=True)
                print("Conversation reset.")
                continue
            elif not user_input:
                continue

            try:
                if streaming:
                    print("\nAssistant: ", end="", flush=True)
                    for chunk in orchestrator.execute_streaming_loop(user_input):
                        print(chunk, end="", flush=True)
                    print()  # New line after streaming
                else:
                    response = orchestrator.execute_loop(user_input)
                    print(f"\nAssistant: {response}")

            except KeyboardInterrupt:
                print("\n\nOperation cancelled.")
                continue
            except Exception as e:
                print(f"\nError: {e}")
                continue

    except KeyboardInterrupt:
        print("\n\nGoodbye!")


def single_shot_mode(prompt: str, llm_client: LLMClient,
                    conversation_manager: ConversationManager,
                    tool_registry: ToolRegistry, streaming: bool = False):
    """Run a single prompt and exit."""
    if streaming:
        orchestrator = StreamingToolOrchestrator(
            llm_client=llm_client,
            conversation_manager=conversation_manager,
            tool_registry=tool_registry
        )
        for chunk in orchestrator.execute_streaming_loop(prompt):
            print(chunk, end="", flush=True)
        print()  # New line after streaming
    else:
        orchestrator = ToolOrchestrator(
            llm_client=llm_client,
            conversation_manager=conversation_manager,
            tool_registry=tool_registry
        )
        response = orchestrator.execute_loop(prompt)
        print(response)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="🐢 Turtle CLI - Multi-API AI coding assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "prompt",
        nargs="?",
        help="Prompt to send to the AI (if not provided, enters interactive mode)"
    )

    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the setup wizard to configure Turtle CLI"
    )

    parser.add_argument(
        "--provider",
        help="Override the AI provider (openai, anthropic, gemini)"
    )

    parser.add_argument(
        "--model",
        help="Override the model to use"
    )

    parser.add_argument(
        "--api-key",
        help="Override the API key"
    )

    parser.add_argument(
        "--stream",
        action="store_true",
        help="Enable streaming mode for real-time responses"
    )

    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    parser.add_argument(
        "--system-prompt",
        help="Set a custom system prompt"
    )

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    setup_logging(args.verbose)

    # Handle setup mode
    if args.setup:
        success = run_forced_setup()
        sys.exit(0 if success else 1)

    # Load configuration
    config = load_config()

    # Override with command line arguments
    if args.provider:
        config['provider'] = args.provider
    if args.model:
        config['model'] = args.model
    if args.api_key:
        config['api_key'] = args.api_key

    # Check if configuration is valid
    if not validate_config(config):
        print("❌ Configuration incomplete!")
        print("Run 'turtle --setup' to configure your AI provider.")
        print("\nOr set environment variables:")
        print("  TURTLE_PROVIDER (openai, anthropic, gemini)")
        print("  TURTLE_MODEL (e.g., gpt-4, claude-3-opus)")
        print("  TURTLE_API_KEY (your API key)")
        sys.exit(1)

    try:
        # Initialize components
        llm_client = LLMClient(
            provider=config['provider'],
            api_key=config['api_key'],
            model=config['model']
        )

        conversation_manager = ConversationManager(
            system_prompt=args.system_prompt,
            max_context_tokens=128000,  # Default context window
            model_name=config['model']
        )

        tool_registry = initialize_tools()

        # Run in appropriate mode
        if args.prompt:
            single_shot_mode(args.prompt, llm_client, conversation_manager,
                           tool_registry, args.stream)
        else:
            interactive_mode(llm_client, conversation_manager, tool_registry,
                           args.stream)

    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        sys.exit(0)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()