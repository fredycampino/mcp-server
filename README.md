# The Fast and Secure Way to Build MCP Servers

This project provide a minimal mcp-server based on **FastMCP** framework that you can run in local.
It's designed to be a robust starting point for any developer looking to expose custom tools to AI agents and LLMs.

## Getting Started

### 1. Clone the repository

```bash
git clone git@github.com:fredycampino/mcp-server.git
cd mcp-server
```

If you're using HTTPS instead of SSH:

```bash
git clone https://github.com/fredycampino/mcp-server.git
```

### 2. Start the virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate   # On Linux/macOS
# Or, on Windows:
.venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Run the server

```bash
python local_mcp.py
```

This will start the FastMCP server at `http://127.0.0.1:7800/mcp` using SSE transport.


## Connecting with CLINE

To use this MCP server with CLINE, follow these steps:

1. Open **CLINE**.
2. Click the **Manage MCP Servers** icon located in the bottom-left corner of the chat interface.
3. Add or modify the configuration in the settings file (named `cline_mcp_settings`) with the following content:

```json
{
  "mcpServers": {
    "local_mcp_server": {
      "disabled": false,
      "timeout": 60,
      "type": "sse",
      "url": "http://127.0.0.1:7800/mcp"
    }
  }
}
```

## Connecting with LM Studio

To connect this MCP server to **LM Studio**, follow these steps:

1. Open **LM Studio**.
2. Open  **PROGRAM** tab, in top rigth side.
3. Click **Install and Open** under the **MCP** section.
4. Opens and modify the `mcp.json` configuration file with the following content:

```json
{
  "mcpServers": {
    "local_mcp_server": {
      "url": "http://127.0.0.1:7800/mcp"
    }
  }
}
```

## Connecting with Cursor

To connect this MCP server to **Cursor**, follow these steps:

1. Open **Cursor**.
2. Go to  **Settings**.
3. Click **tools & Integrations**.
4. Click in new MCP server and edit the `mcp.json` file:

```json
{
  "mcpServers": {
    "local_mcp_server": {
      "url": "http://127.0.0.1:7800/mcp"
    }
  }
}
```

## Add Your Own Tool Module

Extending the server with your own tools is straightforward. Here’s how to add a new module called `x_tools.py`:

**Step 1: Create the tool file**

Create a new file `tools/x_tools.py`. Define your functions inside it. Remember that they can be `async` or regular functions.

```python
# in tools/x_tools.py

import asyncio

async def get_server_info():
    """A new tool to get server information."""
    # Simulate an async operation
    await asyncio.sleep(0.1) 
    return {"server_name": "MyMCP", "version": "1.0.0"}

def get_user_id():
    """A simple sync tool."""
    return {"user_id": "user-12345"}
```

**Step 2: Register the new tools in `local_mcp.py`**

Open `local_mcp.py` and import your new functions. Then, add them to the `TOOLS` list to be automatically registered when the server starts.

```python
# in local_mcp.py

from fastmcp import FastMCP

# ... other imports
from tools.x_tools import get_server_info, get_user_id # 👈 Import your new functions

# ...

# List of imported tool callables to expose
TOOLS = [
    internet_research,
    get_url,
    # ... other tools
    get_server_info, # 👈 Add your new function
    get_user_id      # 👈 Add your other new function
]
```
