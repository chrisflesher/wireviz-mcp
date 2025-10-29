# Gemini Code Assistant Context

## Project Overview

This project is a Python-based server that uses the `wireviz` and `fastmcp` libraries to provide a tool for creating wire harness PDFs from WireViz YAML files. The server exposes a single tool, `create_wire_harness_pdf`, which takes an input YAML file and an output PDF file path as arguments.

The core logic is implemented in `src/wireviz_mcp/server.py`. The project is configured using `pyproject.toml`.

## Building and Running

To build and install the project, you can use a standard Python packaging tool that supports `pyproject.toml`, such as `pip` or `hatch`.

To run the server, execute the following command:

```bash
wireviz-mcp-server
```

## Development Conventions

The codebase follows standard Python conventions. The project uses type hints and has a clear and concise structure.
