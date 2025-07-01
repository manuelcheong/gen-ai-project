import asyncio
import json
from mcp import stdio_client, StdioServerParameters
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from strands_tools import current_time
from strands.models import BedrockModel
from typing import Dict, Any

bedrock_model = BedrockModel(
    model_id="anthropic.claude-3-5-sonnet-20241022-v2:0",
    region_name='us-west-2',  # Change to your preferred region
    temperature=0.3,
)

async def create_location_agent():
    """Create a Strands agent with AWS Location MCP tools"""
    
    # Connect to AWS Location MCP server
    location_mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx", 
            args=["awslabs.aws-location-mcp-server@latest"]
        )
    ))
    
    with location_mcp_client:
        # Get location tools from MCP server
        location_tools = location_mcp_client.list_tools_sync()
        
        # Add custom location-aware tools
        @tool
        def get_user_context() -> str:
            """Get current user context including time and location preferences"""
            return "User prefers locations within 10 miles, current session started recently"
        
        # Combine MCP location tools with custom tools
        all_tools = [current_time, get_user_context] + location_tools
        
        # Create agent with location capabilities
        agent = Agent(
            model=bedrock_model,
            tools=all_tools,
            system_prompt="""You are a helpful location-aware assistant with access to:
            - Geocoding and reverse geocoding services
            - Place search and discovery
            - Route calculation and optimization
            - Real-time location data
            
            Help users find places, get directions, and discover locations based on their needs.
            Always consider distance, travel time, and user preferences when making recommendations."""
        )
        
        return agent
    


async def handler(event: Dict[str, Any], _context) -> str:
    agent = await create_location_agent()
    print("Location agent created successfully!")
    examples = [
        "Find coffee shops Puerta del Sol, Madrid, Spain",
        "What's the address of coordinates 47.6062, -122.3321?",
        "Optimize my route to visit 3 locations: Starbucks, grocery store, and gas station near my location"
    ]
    
    for query in examples:
        print(f"\n🗺️  Query: {query}")
        try:
            response = agent(query)
            print(f"📍 Response: {response.message}")

        except Exception as e:
            print(f"❌ Error: {e}")

    return "true"

