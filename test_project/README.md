# Test Agent

An autonomous AI agent project based on the 'autonomous_agent' template.

## Overview

This project was created using the Claude Code Global Configuration Framework.

## Quick Start

1. **Configure environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and settings
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the agent**:
   ```bash
   python main.py
   ```

## Project Structure

- `agent_config.json` - Agent configuration and capabilities
- `main.py` - Main agent entry point
- `components/` - Reusable agent components
- `mcp_servers.json` - MCP server configurations
- `.env` - Environment variables (create from template)

## Configuration

The agent can be configured through:
- Environment variables in `.env`
- Agent settings in `agent_config.json`
- MCP server settings in `mcp_servers.json`

## Components

This project includes the following components:
- **Memory Management** - Persistent memory and context retention
- **Task Planning** - Multi-step planning and execution
- **Self-Reflection** - Learning and improvement capabilities
- **Common Tools** - File operations, web search, data processing
- **MCP Integration** - Model Context Protocol server management

## Usage

[Add specific usage instructions for your agent here]

## Development

[Add development guidelines and contribution instructions here]
