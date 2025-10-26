"""Simple validation script to test the HubSpot MCP server without pytest."""

import sys
import os
from unittest.mock import AsyncMock, MagicMock, patch

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from hubspot_mcp.server import HubSpotClient, HubSpotConfig, MCPServer


def test_config():
    """Test HubSpot configuration."""
    print("Testing HubSpotConfig...")
    
    config = HubSpotConfig(api_key="test_key")
    assert config.api_key == "test_key"
    assert config.api_base_url == "https://api.hubapi.com"
    
    config2 = HubSpotConfig(access_token="test_token")
    assert config2.access_token == "test_token"
    assert config2.api_key is None
    
    print("✓ HubSpotConfig tests passed")


def test_client_initialization():
    """Test HubSpot client initialization."""
    print("Testing HubSpotClient initialization...")
    
    config = HubSpotConfig(api_key="test_key")
    client = HubSpotClient(config)
    
    assert client.config == config
    assert client.base_url == config.api_base_url
    assert "Content-Type" in client.headers
    assert client.headers["Authorization"] == "Bearer test_key"
    
    print("✓ HubSpotClient initialization tests passed")


def test_client_headers():
    """Test client header generation."""
    print("Testing client headers...")
    
    # Test with access token
    config1 = HubSpotConfig(access_token="test_token")
    client1 = HubSpotClient(config1)
    assert client1.headers["Authorization"] == "Bearer test_token"
    
    # Test with API key
    config2 = HubSpotConfig(api_key="test_key")
    client2 = HubSpotClient(config2)
    assert client2.headers["Authorization"] == "Bearer test_key"
    
    print("✓ Client header tests passed")


def test_server_initialization():
    """Test MCP server initialization."""
    print("Testing MCPServer initialization...")
    
    with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}):
        server = MCPServer()
        
        assert server.config is not None
        assert server.client is not None
        assert len(server.tools) > 0
        
        # Check essential tools are registered
        required_tools = [
            "list_contacts", "get_contact", "create_contact", "update_contact",
            "list_companies", "get_company", "create_company",
            "list_deals", "search"
        ]
        
        for tool in required_tools:
            assert tool in server.tools, f"Tool {tool} not registered"
            assert "description" in server.tools[tool]
            assert "parameters" in server.tools[tool]
            assert "handler" in server.tools[tool]
    
    print("✓ MCPServer initialization tests passed")


def test_get_available_tools():
    """Test get_available_tools method."""
    print("Testing get_available_tools...")
    
    with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}):
        server = MCPServer()
        tools = server.get_available_tools()
        
        assert len(tools) > 0
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
    
    print("✓ get_available_tools tests passed")


def test_tool_parameters():
    """Test that tools have proper parameter definitions."""
    print("Testing tool parameter definitions...")
    
    with patch.dict(os.environ, {"HUBSPOT_API_KEY": "test_key"}):
        server = MCPServer()
        
        # Test list_contacts parameters
        list_contacts = server.tools["list_contacts"]
        params = list_contacts["parameters"]
        assert params["type"] == "object"
        assert "properties" in params
        
        # Test create_contact parameters
        create_contact = server.tools["create_contact"]
        params = create_contact["parameters"]
        assert "email" in params["properties"]
        assert params["required"] == ["email"]
        
        # Test search parameters
        search_tool = server.tools["search"]
        params = search_tool["parameters"]
        assert "object_type" in params["properties"]
        assert "property" in params["properties"]
        assert "value" in params["properties"]
    
    print("✓ Tool parameter tests passed")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("Running HubSpot MCP Server Validation Tests")
    print("="*60 + "\n")
    
    try:
        test_config()
        test_client_initialization()
        test_client_headers()
        test_server_initialization()
        test_get_available_tools()
        test_tool_parameters()
        
        print("\n" + "="*60)
        print("✓ All tests passed successfully!")
        print("="*60 + "\n")
        return 0
    
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
