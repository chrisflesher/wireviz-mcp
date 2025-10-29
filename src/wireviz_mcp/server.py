"""WireViz MCP Server using FastMCP."""

import pathlib

import fastmcp
import wireviz.wireviz
import wireviz.wv_helper

mcp = fastmcp.FastMCP('WireViz MCP Server')


@mcp.tool()
def create_wire_harness_pdf(input_path: pathlib.Path, output_path: pathlib.Path) -> None:
    """Create a wire harness image from a WireViz YAML file.

    Args:
        input_path: Input filename, WireViz YAML format
        output_path: Output filename, PDF format
    """
    yaml_input = wireviz.wv_helper.file_read_text(input_path)
    wireviz.wireviz.parse(
        yaml_input,
        output_formats=['pdf'],
        output_dir=output_path.parent,
        output_name=output_path.stem)


def main():
    """Run the main loop."""
    mcp.run()


if __name__ == '__main__':
    main()
