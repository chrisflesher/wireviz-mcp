"""WireViz MCP Server using FastMCP.

Typical Workflow:
1. Use concept_to_mermaid and mermaid_to_svg to generate a SVG, ask the user to approve it
2. Use harness_to_wireviz and wireviz_to_png to generate a PNG, ask the user to approve it
3. Use wireviz_to_bom to generate a BOM file (TSV)
4. Provide the user with links to final output files (WireViz YAML, TSV, and PNG)
"""

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
def mermaid_to_svg(mermaid_str: str) -> fastmcp.utilities.types.Image:
    """Create a PNG image from a Mermaid diagram string."""
    svg_bytes = mermaidx.to_svg(mermaid_str).encode("utf-8")
    return fastmcp.utilities.types.Image(data=svg_bytes, format='svg+xml')


def main():
    """Run the main loop."""
    mcp.run()


if __name__ == '__main__':
    main()
