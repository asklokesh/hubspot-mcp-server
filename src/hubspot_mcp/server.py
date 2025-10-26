"""HubSpot MCP Server - Main server implementation."""

import asyncio
import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import httpx
from pydantic import Field
from pydantic_settings import BaseSettings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HubSpotConfig(BaseSettings):
    """Configuration for HubSpot API."""
    
    api_key: Optional[str] = Field(None, alias="HUBSPOT_API_KEY")
    access_token: Optional[str] = Field(None, alias="HUBSPOT_ACCESS_TOKEN")
    api_base_url: str = Field("https://api.hubapi.com", alias="HUBSPOT_API_BASE_URL")
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",
        "populate_by_name": True
    }


class HubSpotClient:
    """Client for interacting with HubSpot API."""
    
    def __init__(self, config: HubSpotConfig):
        self.config = config
        self.base_url = config.api_base_url
        self.headers = self._get_headers()
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers=self.headers
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests."""
        headers = {
            "Content-Type": "application/json",
        }
        
        if self.config.access_token:
            headers["Authorization"] = f"Bearer {self.config.access_token}"
        elif self.config.api_key:
            # API key can be used as query parameter or header
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        
        return headers
    
    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make an API request to HubSpot."""
        url = urljoin(self.base_url, endpoint)
        
        # Add API key to params if using API key authentication
        if self.config.api_key and not self.config.access_token:
            params = params or {}
            params["hapikey"] = self.config.api_key
        
        try:
            response = await self.client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
            )
            response.raise_for_status()
            
            if response.status_code == 204:
                return {"success": True, "message": "Operation completed successfully"}
            
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Error making request: {str(e)}")
            raise
    
    async def get_contacts(
        self,
        limit: int = 100,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get contacts from HubSpot."""
        params = {"limit": limit}
        if properties:
            params["properties"] = ",".join(properties)
        
        return await self._request("GET", "/crm/v3/objects/contacts", params=params)
    
    async def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """Get a single contact by ID."""
        return await self._request("GET", f"/crm/v3/objects/contacts/{contact_id}")
    
    async def create_contact(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new contact."""
        return await self._request(
            "POST",
            "/crm/v3/objects/contacts",
            json_data={"properties": properties}
        )
    
    async def update_contact(
        self,
        contact_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a contact."""
        return await self._request(
            "PATCH",
            f"/crm/v3/objects/contacts/{contact_id}",
            json_data={"properties": properties}
        )
    
    async def delete_contact(self, contact_id: str) -> Dict[str, Any]:
        """Delete a contact."""
        return await self._request("DELETE", f"/crm/v3/objects/contacts/{contact_id}")
    
    async def get_companies(
        self,
        limit: int = 100,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get companies from HubSpot."""
        params = {"limit": limit}
        if properties:
            params["properties"] = ",".join(properties)
        
        return await self._request("GET", "/crm/v3/objects/companies", params=params)
    
    async def get_company(self, company_id: str) -> Dict[str, Any]:
        """Get a single company by ID."""
        return await self._request("GET", f"/crm/v3/objects/companies/{company_id}")
    
    async def create_company(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new company."""
        return await self._request(
            "POST",
            "/crm/v3/objects/companies",
            json_data={"properties": properties}
        )
    
    async def update_company(
        self,
        company_id: str,
        properties: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update a company."""
        return await self._request(
            "PATCH",
            f"/crm/v3/objects/companies/{company_id}",
            json_data={"properties": properties}
        )
    
    async def get_deals(
        self,
        limit: int = 100,
        properties: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Get deals from HubSpot."""
        params = {"limit": limit}
        if properties:
            params["properties"] = ",".join(properties)
        
        return await self._request("GET", "/crm/v3/objects/deals", params=params)
    
    async def get_deal(self, deal_id: str) -> Dict[str, Any]:
        """Get a single deal by ID."""
        return await self._request("GET", f"/crm/v3/objects/deals/{deal_id}")
    
    async def create_deal(self, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new deal."""
        return await self._request(
            "POST",
            "/crm/v3/objects/deals",
            json_data={"properties": properties}
        )
    
    async def search(
        self,
        object_type: str,
        filters: List[Dict[str, Any]],
        limit: int = 100,
    ) -> Dict[str, Any]:
        """Search for objects in HubSpot."""
        json_data = {
            "filterGroups": [{"filters": filters}],
            "limit": limit
        }
        return await self._request(
            "POST",
            f"/crm/v3/objects/{object_type}/search",
            json_data=json_data
        )
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


class MCPServer:
    """Model Context Protocol Server for HubSpot."""
    
    def __init__(self):
        self.config = HubSpotConfig()
        self.client = HubSpotClient(self.config)
        self.tools = self._register_tools()
    
    def _register_tools(self) -> Dict[str, Any]:
        """Register available MCP tools."""
        return {
            "list_contacts": {
                "description": "List contacts from HubSpot CRM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of contacts to retrieve",
                            "default": 100
                        },
                        "properties": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of properties to retrieve for each contact"
                        }
                    }
                },
                "handler": self._handle_list_contacts
            },
            "get_contact": {
                "description": "Get a specific contact by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_id": {
                            "type": "string",
                            "description": "The ID of the contact to retrieve"
                        }
                    },
                    "required": ["contact_id"]
                },
                "handler": self._handle_get_contact
            },
            "create_contact": {
                "description": "Create a new contact in HubSpot",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the contact"
                        },
                        "firstname": {
                            "type": "string",
                            "description": "First name of the contact"
                        },
                        "lastname": {
                            "type": "string",
                            "description": "Last name of the contact"
                        },
                        "properties": {
                            "type": "object",
                            "description": "Additional properties for the contact"
                        }
                    },
                    "required": ["email"]
                },
                "handler": self._handle_create_contact
            },
            "update_contact": {
                "description": "Update an existing contact",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "contact_id": {
                            "type": "string",
                            "description": "The ID of the contact to update"
                        },
                        "properties": {
                            "type": "object",
                            "description": "Properties to update"
                        }
                    },
                    "required": ["contact_id", "properties"]
                },
                "handler": self._handle_update_contact
            },
            "list_companies": {
                "description": "List companies from HubSpot CRM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of companies to retrieve",
                            "default": 100
                        }
                    }
                },
                "handler": self._handle_list_companies
            },
            "get_company": {
                "description": "Get a specific company by ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "company_id": {
                            "type": "string",
                            "description": "The ID of the company to retrieve"
                        }
                    },
                    "required": ["company_id"]
                },
                "handler": self._handle_get_company
            },
            "create_company": {
                "description": "Create a new company in HubSpot",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "Name of the company"
                        },
                        "properties": {
                            "type": "object",
                            "description": "Additional properties for the company"
                        }
                    },
                    "required": ["name"]
                },
                "handler": self._handle_create_company
            },
            "list_deals": {
                "description": "List deals from HubSpot CRM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of deals to retrieve",
                            "default": 100
                        }
                    }
                },
                "handler": self._handle_list_deals
            },
            "search": {
                "description": "Search for objects in HubSpot CRM",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "object_type": {
                            "type": "string",
                            "description": "Type of object to search (contacts, companies, deals)",
                            "enum": ["contacts", "companies", "deals"]
                        },
                        "property": {
                            "type": "string",
                            "description": "Property to search on"
                        },
                        "value": {
                            "type": "string",
                            "description": "Value to search for"
                        },
                        "operator": {
                            "type": "string",
                            "description": "Search operator",
                            "default": "EQ",
                            "enum": ["EQ", "NEQ", "LT", "LTE", "GT", "GTE", "CONTAINS"]
                        }
                    },
                    "required": ["object_type", "property", "value"]
                },
                "handler": self._handle_search
            }
        }
    
    async def _handle_list_contacts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_contacts tool call."""
        limit = params.get("limit", 100)
        properties = params.get("properties")
        return await self.client.get_contacts(limit=limit, properties=properties)
    
    async def _handle_get_contact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_contact tool call."""
        contact_id = params["contact_id"]
        return await self.client.get_contact(contact_id)
    
    async def _handle_create_contact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_contact tool call."""
        properties = params.get("properties", {})
        
        # Add email, firstname, lastname to properties if provided
        if "email" in params:
            properties["email"] = params["email"]
        if "firstname" in params:
            properties["firstname"] = params["firstname"]
        if "lastname" in params:
            properties["lastname"] = params["lastname"]
        
        return await self.client.create_contact(properties)
    
    async def _handle_update_contact(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle update_contact tool call."""
        contact_id = params["contact_id"]
        properties = params["properties"]
        return await self.client.update_contact(contact_id, properties)
    
    async def _handle_list_companies(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_companies tool call."""
        limit = params.get("limit", 100)
        return await self.client.get_companies(limit=limit)
    
    async def _handle_get_company(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle get_company tool call."""
        company_id = params["company_id"]
        return await self.client.get_company(company_id)
    
    async def _handle_create_company(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle create_company tool call."""
        properties = params.get("properties", {})
        
        # Add name to properties if provided
        if "name" in params:
            properties["name"] = params["name"]
        
        return await self.client.create_company(properties)
    
    async def _handle_list_deals(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle list_deals tool call."""
        limit = params.get("limit", 100)
        return await self.client.get_deals(limit=limit)
    
    async def _handle_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search tool call."""
        object_type = params["object_type"]
        filters = [{
            "propertyName": params["property"],
            "operator": params.get("operator", "EQ"),
            "value": params["value"]
        }]
        limit = params.get("limit", 100)
        return await self.client.search(object_type, filters, limit)
    
    async def handle_tool_call(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call from the MCP client."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool = self.tools[tool_name]
        handler = tool["handler"]
        
        try:
            result = await handler(params)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {str(e)}")
            return {"success": False, "error": str(e)}
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools."""
        return [
            {
                "name": name,
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for name, tool in self.tools.items()
        ]
    
    async def run_stdio(self):
        """Run the server in stdio mode for MCP communication."""
        logger.info("Starting HubSpot MCP Server in stdio mode")
        
        # In a real MCP server, this would handle JSON-RPC over stdio
        # For now, this is a placeholder that shows the structure
        try:
            # Print available tools
            tools = self.get_available_tools()
            logger.info(f"Registered {len(tools)} tools")
            
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        finally:
            await self.client.close()
    
    async def close(self):
        """Close the server and cleanup resources."""
        await self.client.close()


def main():
    """Main entry point for the MCP server."""
    server = MCPServer()
    
    try:
        asyncio.run(server.run_stdio())
    except KeyboardInterrupt:
        logger.info("Server stopped")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
