"""WireViz MCP Server using FastMCP."""

import typing

import fastmcp
import fastmcp.utilities.types
import mcp.types as mcp_types
import wireviz.wireviz
import yaml

mcp = fastmcp.FastMCP('WireViz MCP Server')


@mcp.tool()
def create_wire_harness_image(yaml_input: str) -> mcp_types.ImageContent:
    """Create a wire harness PNG image from a WireViz YAML text file.

    Args:
        yaml_input: WireViz YAML format

    Returns:
        Wire harness PNG image.
    """
    result = wireviz.wireviz.parse(yaml_input, return_types=['png'])
    return fastmcp.utilities.types.Image(data=result[0], format='PNG')


@mcp.tool()
def create_wire_harness_yaml(
        connectors: typing.Dict[str, typing.Dict[str, str]],
        cables: typing.Dict[str, typing.Dict[str, typing.Any]],
        connections: typing.List[typing.List[typing.Dict[str, typing.Any]]],
        ) -> str:
    """Create WireViz YAML text.

    connectors: Dictionary of unique connector designator (e.g. X1, X2, etc.) to
        attributes. Valid attribues are type, subtype, color, and image.
    cables: Dictionary of unique cable designator (e.g. W1, W2, etc.) to
        attributes. Valid attributes are category, type, gauge [AWG or mm2],
        length [m or ft], shield, color, image, manufacturer, mpn, wirecount,
        colors, and image
    connections: Dictionary of unique identifiers to either 1) connector pin or
        2) cable wire numbers

    This content should always be written to disk.
    """
    result = {
        connectors: connectors,
        cables: cables,
        connections: connections,
    }
    return yaml.dumps(result)


def main():
    """Run the main loop."""
    mcp.run()


if __name__ == '__main__':
    main()
