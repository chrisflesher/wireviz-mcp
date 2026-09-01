"""WireViz MCP Server using FastMCP."""

import fastmcp
import fastmcp.utilities.types
import mermaidx

import wireviz_mcp.common


mcp = fastmcp.FastMCP('WireViz MCP Server')
mcp.add_tool(wireviz_mcp.common.concept_to_mermaid)
mcp.add_tool(wireviz_mcp.common.harness_to_wireviz)
mcp.add_tool(wireviz_mcp.common.wireviz_to_bom)


@mcp.tool()
def wireviz_to_png(wireviz_yaml: str) -> fastmcp.utilities.types.Image:
    """Create a PNG image from a harness definition."""
    png_bytes = wireviz_mcp.common.wireviz_to_png(wireviz_yaml)
    return fastmcp.utilities.types.Image(data=png_bytes, format='png')


@mcp.tool()
def mermaid_to_png(mermaid_str: str) -> fastmcp.utilities.types.Image:
    """Create a PNG image from a Mermaid diagram string."""
    png_bytes = mermaidx.render(mermaid_str).png()
    return fastmcp.utilities.types.Image(data=png_bytes, format='png')


def main():
    """Run the main loop."""
    mcp.run()


if __name__ == '__main__':
    main()
