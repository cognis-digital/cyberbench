"""CYBERBENCH MCP server — exposes scan() as an MCP tool for Cognis.Studio."""
from __future__ import annotations
from cyberbench.core import scan, to_json

def serve() -> int:
    """Start an MCP stdio server. Requires the optional 'mcp' extra:
        pip install "cognis-cyberbench[mcp]"
    """
    try:
        from mcp.server.fastmcp import FastMCP
    except Exception:
        print("Install the MCP extra: pip install 'cognis-cyberbench[mcp]'")
        return 1
    app = FastMCP("cyberbench")

    @app.tool()
    def cyberbench_scan(target: str) -> str:
        """Chainable encode/decode/transform pipeline (base64/hex/rot/xor/url/gzip). Returns JSON findings."""
        return to_json(scan(target))

    app.run()
    return 0
