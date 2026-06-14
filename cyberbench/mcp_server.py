"""CYBERBENCH MCP server — exposes run() and magic() as MCP tools."""
from __future__ import annotations

import json

from cyberbench.core import magic
from cyberbench.core import run


def serve() -> int:
    """Start an MCP stdio server.  Requires the optional 'mcp' extra:
        pip install "cognis-cyberbench[mcp]"
    """
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore[import]
    except ImportError:
        print("Install the MCP extra: pip install 'cognis-cyberbench[mcp]'")
        return 1
    app = FastMCP("cyberbench")

    @app.tool()
    def cyberbench_run(data: str, recipe: str) -> str:
        """Apply a comma-separated recipe of ops to data.  Returns the transformed bytes as a string."""
        ops = [op.strip() for op in recipe.split(",") if op.strip()]
        result = run(data.encode(), ops)
        return result.decode("utf-8", "replace")

    @app.tool()
    def cyberbench_magic(data: str) -> str:
        """Auto-detect encoding of data.  Returns JSON list of {recipe, preview} dicts."""
        return json.dumps(magic(data.encode()), indent=2)

    app.run()
    return 0
