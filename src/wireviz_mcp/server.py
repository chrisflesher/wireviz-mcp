"""WireViz MCP Server using FastMCP."""

import fastmcp

import wireviz_mcp.common


mcp = fastmcp.FastMCP('WireViz MCP Server')
mcp.add_tool(wireviz_mcp.common.concept_to_mermaid)
mcp.add_tool(wireviz_mcp.common.harness_to_wireviz)
mcp.add_tool(wireviz_mcp.common.wireviz_to_bom)
mcp.add_tool(wireviz_mcp.common.wireviz_to_png)


def main():
    """Run the main loop."""
    mcp.run()


if __name__ == '__main__':
    main()
