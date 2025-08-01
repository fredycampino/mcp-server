"""Main entry-point for the MCP server.

Initialises FastMCP, registers all tools, and starts the HTTP-stream transport.

Run with:
    python local_mcp.py
and register the endpoint in LM Studio as:
    http://127.0.0.1:7800/mcp
"""

from fastmcp import FastMCP

# ──────────────────────────
# Third-party / shared tools
# ──────────────────────────

from tools.internet_tools import internet_research,get_url
from tools.file_tools import list_files, read_file, overwrite_file, create_file


# List of imported tool callables to expose (easy to reorder / filter)
TOOLS = [
    internet_research,
    get_url,
    list_files,
    read_file,
    overwrite_file,
    create_file
]

# ──────────────────────────
# FastMCP application
# ──────────────────────────

mcp = FastMCP("hello")

# ──────────────────────────
# Tool registration
# ──────────────────────────


@mcp.tool()
async def greet(name: str = "world") -> dict:
    """Return a friendly greeting as a JSON object."""
    return {"greeting": f"Hello, {name}!", "recipient": name}


# Register each imported tool once
for fn in TOOLS:
    mcp.tool()(fn)

# ──────────────────────────
# Entry-point
# ──────────────────────────

if __name__ == "__main__":
    mcp.run(
        transport="sse",
        host="127.0.0.1",
        port=7800,
        path="/mcp",
    )
