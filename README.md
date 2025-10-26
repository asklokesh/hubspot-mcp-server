# HubSpot MCP Server

<div align="center">

# Hubspot Mcp Server

[![GitHub stars](https://img.shields.io/github/stars/LokiMCPUniverse/hubspot-mcp-server?style=social)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/LokiMCPUniverse/hubspot-mcp-server?style=social)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/network)
[![GitHub watchers](https://img.shields.io/github/watchers/LokiMCPUniverse/hubspot-mcp-server?style=social)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/watchers)

[![License](https://img.shields.io/github/license/LokiMCPUniverse/hubspot-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/LokiMCPUniverse/hubspot-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/LokiMCPUniverse/hubspot-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/pulls)
[![Last Commit](https://img.shields.io/github/last-commit/LokiMCPUniverse/hubspot-mcp-server?style=for-the-badge)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/commits)

[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![MCP](https://img.shields.io/badge/Model_Context_Protocol-DC143C?style=for-the-badge)](https://modelcontextprotocol.io)
[![CI](https://github.com/asklokesh/hubspot-mcp-server/actions/workflows/ci.yml/badge.svg)](https://github.com/asklokesh/hubspot-mcp-server/actions/workflows/ci.yml)

[![Commit Activity](https://img.shields.io/github/commit-activity/m/LokiMCPUniverse/hubspot-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/pulse)
[![Code Size](https://img.shields.io/github/languages/code-size/LokiMCPUniverse/hubspot-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/hubspot-mcp-server)
[![Contributors](https://img.shields.io/github/contributors/LokiMCPUniverse/hubspot-mcp-server?style=flat-square)](https://github.com/LokiMCPUniverse/hubspot-mcp-server/graphs/contributors)

</div>

A Model Context Protocol (MCP) server for integrating HubSpot with GenAI applications.

## Overview

CRM, Marketing, Sales and Service Hub integration

## Features

- Comprehensive HubSpot API coverage
- Multiple authentication methods
- Enterprise-ready with rate limiting
- Full error handling and retry logic
- Async support for better performance

## Installation

```bash
pip install hubspot-mcp-server
```

Or install from source:

```bash
git clone https://github.com/asklokesh/hubspot-mcp-server.git
cd hubspot-mcp-server
pip install -e .
```

## Configuration

Create a `.env` file or set environment variables according to HubSpot API requirements.

## Quick Start

### Installation

```bash
pip install hubspot-mcp-server
```

Or install from source:

```bash
git clone https://github.com/asklokesh/hubspot-mcp-server.git
cd hubspot-mcp-server
pip install -e .
```

### Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Add your HubSpot credentials to `.env`:
```bash
# Option 1: Use API Key (Legacy)
HUBSPOT_API_KEY=your_api_key_here

# Option 2: Use Access Token (Recommended)
HUBSPOT_ACCESS_TOKEN=your_access_token_here
```

### Usage

```python
import asyncio
from hubspot_mcp.server import MCPServer

async def main():
    # Initialize the server
    server = MCPServer()
    
    # Get available tools
    tools = server.get_available_tools()
    print(f"Available tools: {[tool['name'] for tool in tools]}")
    
    # Example: List contacts
    result = await server.handle_tool_call("list_contacts", {"limit": 10})
    print(result)
    
    # Clean up
    await server.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Available Tools

The MCP server provides the following tools:

- **Contacts**: `list_contacts`, `get_contact`, `create_contact`, `update_contact`
- **Companies**: `list_companies`, `get_company`, `create_company`, `update_company`
- **Deals**: `list_deals`, `get_deal`, `create_deal`
- **Search**: `search` - Search across contacts, companies, and deals

### Running Tests

```bash
# Simple validation tests (no dependencies required)
python tests/test_simple.py

# Full test suite (requires pytest)
pip install -e ".[dev]"
pytest
```

### Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linting
ruff check src/ tests/

# Run formatting
ruff format src/ tests/
```

## License

MIT License - see LICENSE file for details
