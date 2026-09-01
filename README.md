# WireViz MCP Server

A Model Context Protocol (MCP) server that integrates [WireViz](https://github.com/formatc1702/WireViz). This allows AI assistants to design and visualize physical wiring harnesses.

## Features

The server exposes the following tools:

- **`concept_to_mermaid`**: Translates a simplified design (`ConceptGraph`) into a Mermaid diagram to help plan the harness design.
- **`harness_to_wireviz`**: Translates a complete harness design (`Harness`) into WireViz YAML.
- **`wireviz_to_bom`**: Generates a Bill of Materials (BOM) in TSV format from WireViz YAML.
- **`wireviz_to_png`**: Renders WireViz YAML as PNG.

## Installation

Edit `mcp_config.json` and add the following:

```
{
  "mcpServers": {
    "wireviz-mcp": {
      "command": "uvx",
      "args": [
        "--from", "git+https://github.com/chrisflesher/wireviz-mcp.git",
        "wireviz-mcp-server"
      ]
    }
  }
}
```

## Workflow Examples

### Example 1

Use wireviz-mcp server to wire a Molex 0039014031 from "Source Device" to "Target Device" with same connector and pinout:
1. 5V (red)
2. PWM (yellow)
3. GND (black)

## Developer

To clone the repo and run unit tests:

```
git clone https://github.com/chrisflesher/wireviz-mcp.git
cd wireviz-mcp
tox
```
