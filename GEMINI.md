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

## WireViz YAML Format

### Bare-bones example

- Minimum working example
- Only 1-to-1 sequential wiring

```
connectors:
  X1:
    pincount: 4
  X2:
    pincount: 4

cables:
  W1:
    wirecount: 4
    length: 1

connections:
  -
    - X1: [1-4]
    - W1: [1-4]
    - X2: [1-4]
```

### Adding parameters and colors

- Parameters for connectors and cables
- Auto-calculate equivalent AWG from mm2
- Non-sequential wiring

```
connectors:
  X1:
    pincount: 4
    # More connector parameters:
    type: Molex KK 254
    subtype: female
  X2:
    pincount: 4
    type: Molex KK 254
    subtype: female

cables:
  W1:
    wirecount: 4
    # more cable parameters:
    length: 1
    gauge: 0.25 mm2
    show_equiv: true # auto-calculate AWG equivalent
    colors: [WH, BN, GN, YE]

connections:
  -
    - X1: [1-4]
    - W1: [1-4]
    # non-sequential wiring:
    - X2: [1,2,4,3]
```

### Pinouts, shielding, templates (I)

- Connector pinouts
- Pincount implicit in pinout
- Cable color codes
- Cable shielding, shield wiring
- Templates

```
connectors:
  X1: &template1 # define a template for later use
    pinlabels: [GND, VCC, RX, TX] # pincount implicit in pinout
    type: Molex KK 254
    subtype: female
  X2:
    <<: *template1 # reuse template

cables:
  W1:
    wirecount: 4
    length: 1
    gauge: 0.25 mm2
    show_equiv: true
    color_code: DIN # auto-assign colors based on DIN 47100
    shield: true # add cable shielding

connections:
  -
    - X1: [1-4]
    - W1: [1-4]
    - X2: [1,2,4,3]
  - # connect the shielding to a pin
    - X1: 1
    - W1: s
```
