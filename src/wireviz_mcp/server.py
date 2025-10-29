"""WireViz MCP Server using FastMCP."""

import typing

import fastmcp
import fastmcp.utilities.types
import mcp.types as mcp_types
import wireviz.wireviz
import wireviz.wv_bom
import wireviz.wv_helper
import yaml

mcp = fastmcp.FastMCP('WireViz MCP Server')


@mcp.tool()
def create_wireviz_bom(wireviz_yaml: str) -> str:
    """Create a WireViz bill of materials from WireViz YAML.

    Args:
        yaml_input: WireViz YAML.

    Returns:
        Wire harness BOM in tab separated value format.
        Always write this to the local file system!
    """
    harness = wireviz.wireviz.parse(wireviz_yaml, return_types=['harness'])
    bomlist = wireviz.wv_bom.bom_list(harness.bom())
    tsv = wireviz.wv_helper.tuplelist2tsv(bomlist)
    return tsv


@mcp.tool()
def create_wireviz_png(wireviz_yaml: str) -> mcp_types.ImageContent:
    """Create a WireViz PNG image from WireViz YAML.

    Args:
        yaml_input: WireViz YAML.

    Returns:
        Wire harness PNG image.
        Always write this to the local file system!
    """
    raw_bytes = wireviz.wireviz.parse(wireviz_yaml, return_types=['png'])
    return fastmcp.utilities.types.Image(data=raw_bytes, format='PNG')


@mcp.tool()
def create_wireviz_yaml(
        connectors: typing.Dict[str, typing.Dict[str, str]],
        cables: typing.Dict[str, typing.Dict[str, typing.Any]],
        connections: typing.List[typing.List[typing.Any]],
        ) -> str:
    """Create WireViz YAML text.

    Args:
        connectors: Dictionary of unique connector designator (e.g. X1, X2) to
            connector attributes (e.g. type, subtype, color, image, notes, pn,
            manufacturer, mpn, pincount, pins, pinlabels, pincolors).
        cables: Dictionary of unique cable designator (e.g. W1, W2) to cable
            attributes (e.g. category, type, gauge, length, shield, color,
            image, notes, pn, manufacturer, mpn, wirecount, colors)
        connections: List of connections to be made between cables and
            connectors

    Returns:
        WireViz YAML text. Always write this to the local filesystem!

    Examples:

    1. Bare-bones example

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

    2. Adding parameters and colors

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

    3. Pinouts, shielding, templates (I)

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

    4. Templates (II), notes, American standards, daisy chaining (I)

    - Overriding template parameters
    - Add nodes to connectors and cables
    - American standards: AWG gauge and IEC colors
    - Linear daisy-chain
    - Convenient for shorter chains

    connectors:
        X1: &template_con
            pinlabels: [GND, VCC, SCL, SDA]
            type: Molex KK 254
            subtype: male
            notes: to microcontroller # add notes
        X2:
            <<: *template_con # use template
            subtype: female   # but override certain parameters
            notes: to accelerometer
        X3:
            <<: *template_con
            subtype: female
            notes: to temperature sensor

    cables:
        W1: &template_cbl
            wirecount: 4
            length: 0.3
            gauge: 24 AWG # specify gauge in AWG directly
            color_code: IEC # IEC 62 colors also supported
            notes: This cable is a bit longer
        W2:
            <<: *template_cbl
            length: 0.1
            notes: This cable is a bit shorter

    connections:
        -
            - X1: [1-4]
            - W1: [1-4]
            - X2: [1-4]
        - # daisy chain connectors (in line)
            - X2: [1-4]
            - W2: [1-4]
            - X3: [1-4]
    """
    result = {
        'connectors': connectors,
        'cables': cables,
        'connections': connections,
    }
    yaml_input = yaml.dump(result)
    return yaml_input


def main():
    """Run the main loop."""
    mcp.run()


if __name__ == '__main__':
    main()
