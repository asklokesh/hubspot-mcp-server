#!/usr/bin/env python3
"""
Demo script showing how to use the HubSpot MCP Server.
This demonstrates the various tools available.
"""

import asyncio
import os
from hubspot_mcp.server import MCPServer


async def demo():
    """Demonstrate the MCP server functionality."""
    print("="*60)
    print("HubSpot MCP Server Demo")
    print("="*60)
    print()
    
    # Check if credentials are configured
    if not os.getenv("HUBSPOT_API_KEY") and not os.getenv("HUBSPOT_ACCESS_TOKEN"):
        print("⚠️  No HubSpot credentials found!")
        print("   Please set HUBSPOT_API_KEY or HUBSPOT_ACCESS_TOKEN")
        print("   in your .env file or environment variables.")
        print()
        print("   Example:")
        print("   export HUBSPOT_ACCESS_TOKEN=your_token_here")
        print()
        return
    
    # Initialize server
    print("Initializing MCP Server...")
    server = MCPServer()
    print("✓ Server initialized successfully")
    print()
    
    # Show available tools
    print("Available Tools:")
    print("-" * 60)
    tools = server.get_available_tools()
    for tool in tools:
        print(f"  • {tool['name']}: {tool['description']}")
    print()
    
    # Example: Try to list contacts (will fail if no valid credentials)
    print("Example: Listing contacts (limit=5)...")
    print("-" * 60)
    try:
        result = await server.handle_tool_call("list_contacts", {"limit": 5})
        if result["success"]:
            data = result["result"]
            if "results" in data:
                print(f"✓ Found {len(data['results'])} contacts")
                for contact in data["results"][:3]:  # Show first 3
                    contact_id = contact.get("id", "N/A")
                    props = contact.get("properties", {})
                    email = props.get("email", "N/A")
                    print(f"  - ID: {contact_id}, Email: {email}")
            else:
                print(f"✓ Response: {data}")
        else:
            print(f"✗ Error: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"✗ Error calling tool: {str(e)}")
    print()
    
    # Clean up
    print("Cleaning up...")
    await server.close()
    print("✓ Server closed")
    print()
    print("="*60)
    print("Demo completed!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(demo())
