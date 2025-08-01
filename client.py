import asyncio
import json
from fastmcp import Client, FastMCP

# In-memory server (ideal for testing)
# server = FastMCP("hello")
# client = Client(server)

# HTTP server
client = Client("http://127.0.0.1:7800/mcp")

# Local Python script
# client = Client("my_mcp_server.py")

async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        print("hola mundo") 
        
        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        tools_data = [tool.model_dump() for tool in tools]  #to dicts
        print(json.dumps(tools_data, indent=2))
      

        # Execute operations
         # result = await client.call_tool("example_tool", {"param": "value"})
         # print(result)

asyncio.run(main())