"""Main entry-point for the MCP server.

Initialises FastMCP, registers all tools, and starts the HTTP-stream transport.

Run with:
    python local_mcp.py
and register the endpoint in LM Studio as:
    http://127.0.0.1:7800/mcp
"""

import os

from fastmcp import FastMCP

# ──────────────────────────
# Third-party / shared tools
# ──────────────────────────

from tools.internet_tools import internet_research, get_url
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
    transport = (os.environ.get("MCP_TRANSPORT") or "sse").strip().lower()

    if transport == "stdio":
        # Important: keep stdout clean (MCP protocol only) for stdio transport.
        mcp.run(transport="stdio", show_banner=False)
    elif transport == "sse":
        mcp.run(
            transport="sse",
            host=os.environ.get("MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("MCP_PORT", "7800")),
            path=os.environ.get("MCP_PATH", "/mcp"),
        )
    elif transport in {"streamable-http", "streamable_http", "streamablehttp"}:
        mcp.run(
            transport="streamable-http",
            host=os.environ.get("MCP_HOST", "127.0.0.1"),
            port=int(os.environ.get("MCP_PORT", "7800")),
            path=os.environ.get("MCP_PATH", "/mcp"),
        )
    else:
        raise SystemExit(
            f"Unsupported MCP_TRANSPORT={transport!r}. Use 'stdio', 'sse', or 'streamable-http'."
        )
