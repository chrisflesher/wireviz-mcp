# WireViz MCP Server

A Model Context Protocol (MCP) server that integrates [WireViz](https://github.com/formatc1702/WireViz). This allows AI assistants to design and visualize physical wiring harnesses.

## Features

The server exposes the following tools:

- **`concept_to_mermaid`**: Translates a simplified design (`ConceptGraph`) into a Mermaid diagram to help plan the harness design.
- **`mermaid_to_svg`**: Renders Mermaid diagram as SVG.
- **`harness_to_wireviz`**: Translates a complete harness design (`Harness`) into WireViz YAML.
- **`wireviz_to_bom`**: Generates a Bill of Materials (BOM) in TSV format from WireViz YAML.
- **`wireviz_to_png`**: Renders WireViz YAML as PNG.

## Installation

### Option 1: pip

Create a virtual environment:

```
python -m venv .venv
.venv/bin/pip install git+https://github.com/chrisflesher/wireviz-mcp.git
```

Edit `mcp_config.json` to add the server:

```
{
  "mcpServers": {
    "wireviz-mcp": {
      "command": ".venv/bin/wireviz-mcp-server",
      "args": []
    }
  }
}
```

### Option 2: uvx

Edit `mcp_config.json` to add the server:

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

## Contributing

To run unit tests:

```
tox
```
