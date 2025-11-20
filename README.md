# Turtle CLI

Multi-API AI coding assistant for your terminal. Connect to Gemini, GPT, Claude, or any LLM provider for agentic coding tasks with tool support.

## Overview

Turtle CLI is a command-line interface that enables AI-powered coding assistance with support for multiple LLM providers. The tool provides a unified interface for interacting with various AI models while maintaining conversation context and supporting tool execution for file operations and command execution.

## Features

- **Multi-Provider Support**: Works with OpenAI, Anthropic Claude, Google Gemini, and any LiteLLM-compatible provider
- **Tool Integration**: Built-in tools for file system operations, command execution, and more
- **Conversation Management**: Persistent conversation history and context management
- **Streaming Support**: Real-time response streaming for better user experience
- **Setup Wizard**: Interactive first-time setup for easy configuration

## Requirements

- Python 3.13 or higher
- Valid API keys for your chosen LLM providers

## Installation

### From Source

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd turtle
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the package:
   ```bash
   pip install -e .
   ```

## Configuration

On first run, Turtle CLI will launch a setup wizard to configure your LLM providers. You can also run setup manually:

```bash
turtle --setup
```

Configuration is stored in the `.turtle` directory in your project root.

## Usage

### Basic Usage

Start a conversation with your configured AI assistant:

```bash
turtle "Help me refactor this function"
```

### Available Options

- `--verbose`: Enable verbose logging
- `--setup`: Run the configuration setup wizard
- `--model`: Specify a particular model to use

## Development

### Setup Development Environment

1. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Run tests with coverage:
   ```bash
   pytest --cov=turtle_cli
   ```

### Project Structure

```
src/turtle_cli/
├── cli.py              # Main CLI entry point
├── llm/                # LLM client and conversation management
├── tools/              # Tool protocol and implementations
└── setup/              # Configuration and setup wizards
```

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## License

Apache-2.0 License - see [LICENSE](LICENSE) file for details.