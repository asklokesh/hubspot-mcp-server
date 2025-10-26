"""Tests for the MCP server."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from hubspot_mcp.server import HubSpotClient, HubSpotConfig, MCPServer


@pytest.fixture
def config():
    """Create a test configuration."""
    return HubSpotConfig(
        api_key="test_api_key",
        api_base_url="https://api.hubapi.com"
    )


@pytest.fixture
def client(config):
    """Create a test HubSpot client."""
    return HubSpotClient(config)


@pytest.fixture
def server():
    """Create a test MCP server."""
    with patch.dict("os.environ", {"HUBSPOT_API_KEY": "test_key"}):
        return MCPServer()


class TestHubSpotConfig:
    """Tests for HubSpotConfig."""
    
    def test_config_with_api_key(self):
        """Test configuration with API key."""
        config = HubSpotConfig(api_key="test_key")
        assert config.api_key == "test_key"
        assert config.api_base_url == "https://api.hubapi.com"
    
    def test_config_with_access_token(self):
        """Test configuration with access token."""
        config = HubSpotConfig(access_token="test_token")
        assert config.access_token == "test_token"
        assert config.api_key is None


class TestHubSpotClient:
    """Tests for HubSpotClient."""
    
    def test_client_initialization(self, client, config):
        """Test client initialization."""
        assert client.config == config
        assert client.base_url == config.api_base_url
        assert "Content-Type" in client.headers
    
    def test_headers_with_access_token(self):
        """Test headers with access token."""
        config = HubSpotConfig(access_token="test_token")
        client = HubSpotClient(config)
        assert client.headers["Authorization"] == "Bearer test_token"
    
    def test_headers_with_api_key(self):
        """Test headers with API key."""
        config = HubSpotConfig(api_key="test_key")
        client = HubSpotClient(config)
        assert client.headers["Authorization"] == "Bearer test_key"
    
    @pytest.mark.asyncio
    async def test_get_contacts_success(self, client):
        """Test successful get_contacts call."""
        mock_response = {
            "results": [
                {"id": "1", "properties": {"email": "test@example.com"}}
            ]
        }
        
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_contacts(limit=10)
            
            assert result == mock_response
            mock_request.assert_called_once_with(
                "GET",
                "/crm/v3/objects/contacts",
                params={"limit": 10}
            )
    
    @pytest.mark.asyncio
    async def test_get_contact_by_id(self, client):
        """Test get_contact by ID."""
        mock_response = {
            "id": "123",
            "properties": {"email": "test@example.com"}
        }
        
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_contact("123")
            
            assert result == mock_response
            mock_request.assert_called_once_with(
                "GET",
                "/crm/v3/objects/contacts/123"
            )
    
    @pytest.mark.asyncio
    async def test_create_contact(self, client):
        """Test create_contact."""
        properties = {"email": "new@example.com", "firstname": "John"}
        mock_response = {"id": "456", "properties": properties}
        
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.create_contact(properties)
            
            assert result == mock_response
            mock_request.assert_called_once_with(
                "POST",
                "/crm/v3/objects/contacts",
                json_data={"properties": properties}
            )
    
    @pytest.mark.asyncio
    async def test_update_contact(self, client):
        """Test update_contact."""
        contact_id = "123"
        properties = {"lastname": "Doe"}
        mock_response = {"id": contact_id, "properties": properties}
        
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.update_contact(contact_id, properties)
            
            assert result == mock_response
            mock_request.assert_called_once_with(
                "PATCH",
                f"/crm/v3/objects/contacts/{contact_id}",
                json_data={"properties": properties}
            )
    
    @pytest.mark.asyncio
    async def test_delete_contact(self, client):
        """Test delete_contact."""
        contact_id = "123"
        mock_response = {"success": True, "message": "Operation completed successfully"}
        
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.delete_contact(contact_id)
            
            assert result == mock_response
            mock_request.assert_called_once_with(
                "DELETE",
                f"/crm/v3/objects/contacts/{contact_id}"
            )
    
    @pytest.mark.asyncio
    async def test_get_companies(self, client):
        """Test get_companies."""
        mock_response = {
            "results": [
                {"id": "1", "properties": {"name": "Test Company"}}
            ]
        }
        
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.get_companies(limit=50)
            
            assert result == mock_response
            mock_request.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_company(self, client):
        """Test create_company."""
        properties = {"name": "New Company"}
        mock_response = {"id": "789", "properties": properties}
        
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.create_company(properties)
            
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_search(self, client):
        """Test search functionality."""
        mock_response = {
            "results": [
                {"id": "1", "properties": {"email": "test@example.com"}}
            ]
        }
        
        filters = [{"propertyName": "email", "operator": "EQ", "value": "test@example.com"}]
        
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response
            
            result = await client.search("contacts", filters, limit=10)
            
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_close(self, client):
        """Test client close."""
        with patch.object(client.client, "aclose", new_callable=AsyncMock) as mock_close:
            await client.close()
            mock_close.assert_called_once()


class TestMCPServer:
    """Tests for MCPServer."""
    
    def test_server_initialization(self, server):
        """Test server initialization."""
        assert server.config is not None
        assert server.client is not None
        assert len(server.tools) > 0
    
    def test_register_tools(self, server):
        """Test tool registration."""
        tools = server.tools
        
        # Check that essential tools are registered
        assert "list_contacts" in tools
        assert "get_contact" in tools
        assert "create_contact" in tools
        assert "update_contact" in tools
        assert "list_companies" in tools
        assert "create_company" in tools
        assert "list_deals" in tools
        assert "search" in tools
        
        # Check tool structure
        for tool_name, tool in tools.items():
            assert "description" in tool
            assert "parameters" in tool
            assert "handler" in tool
    
    def test_get_available_tools(self, server):
        """Test get_available_tools."""
        tools = server.get_available_tools()
        
        assert len(tools) > 0
        
        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "parameters" in tool
    
    @pytest.mark.asyncio
    async def test_handle_list_contacts(self, server):
        """Test handle_tool_call for list_contacts."""
        mock_result = {"results": [{"id": "1"}]}
        
        with patch.object(server.client, "get_contacts", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_result
            
            result = await server.handle_tool_call("list_contacts", {"limit": 10})
            
            assert result["success"] is True
            assert result["result"] == mock_result
    
    @pytest.mark.asyncio
    async def test_handle_get_contact(self, server):
        """Test handle_tool_call for get_contact."""
        mock_result = {"id": "123", "properties": {"email": "test@example.com"}}
        
        with patch.object(server.client, "get_contact", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_result
            
            result = await server.handle_tool_call("get_contact", {"contact_id": "123"})
            
            assert result["success"] is True
            assert result["result"] == mock_result
    
    @pytest.mark.asyncio
    async def test_handle_create_contact(self, server):
        """Test handle_tool_call for create_contact."""
        mock_result = {"id": "456"}
        params = {
            "email": "new@example.com",
            "firstname": "John",
            "lastname": "Doe"
        }
        
        with patch.object(server.client, "create_contact", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_result
            
            result = await server.handle_tool_call("create_contact", params)
            
            assert result["success"] is True
            assert result["result"] == mock_result
    
    @pytest.mark.asyncio
    async def test_handle_update_contact(self, server):
        """Test handle_tool_call for update_contact."""
        mock_result = {"id": "123"}
        params = {
            "contact_id": "123",
            "properties": {"lastname": "Smith"}
        }
        
        with patch.object(server.client, "update_contact", new_callable=AsyncMock) as mock_update:
            mock_update.return_value = mock_result
            
            result = await server.handle_tool_call("update_contact", params)
            
            assert result["success"] is True
            assert result["result"] == mock_result
    
    @pytest.mark.asyncio
    async def test_handle_search(self, server):
        """Test handle_tool_call for search."""
        mock_result = {"results": [{"id": "1"}]}
        params = {
            "object_type": "contacts",
            "property": "email",
            "value": "test@example.com",
            "operator": "EQ"
        }
        
        with patch.object(server.client, "search", new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_result
            
            result = await server.handle_tool_call("search", params)
            
            assert result["success"] is True
            assert result["result"] == mock_result
    
    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self, server):
        """Test handle_tool_call with unknown tool."""
        with pytest.raises(ValueError, match="Unknown tool"):
            await server.handle_tool_call("unknown_tool", {})
    
    @pytest.mark.asyncio
    async def test_handle_tool_call_error(self, server):
        """Test handle_tool_call with error."""
        with patch.object(server.client, "get_contacts", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("API Error")
            
            result = await server.handle_tool_call("list_contacts", {"limit": 10})
            
            assert result["success"] is False
            assert "error" in result
            assert "API Error" in result["error"]
    
    @pytest.mark.asyncio
    async def test_close(self, server):
        """Test server close."""
        with patch.object(server.client, "close", new_callable=AsyncMock) as mock_close:
            await server.close()
            mock_close.assert_called_once()
