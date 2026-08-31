"""WireViz model."""

import enum
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile
import typing

import yaml
from pydantic import BaseModel, Field, model_validator


class Color(enum.Enum):
    """Color.

    These are DIN 47100 standard German abbreviations.
    """

    # Core 1-10: Solid Colors
    WHITE = 'WH'
    BROWN = 'BN'
    GREEN = 'GN'
    YELLOW = 'YE'
    GREY = 'GY'
    PINK = 'PK'
    BLUE = 'BU'
    RED = 'RD'
    BLACK = 'BK'
    VIOLET = 'VT'

    # Core 11-44: Two-Color Combinations (Base/Ring)
    GREY_PINK = 'GYPK'
    RED_BLUE = 'RDBU'
    WHITE_GREEN = 'WHGN'
    BROWN_GREEN = 'BNGN'
    WHITE_YELLOW = 'WHYE'
    YELLOW_BROWN = 'YEBN'
    WHITE_GREY = 'WHGY'
    GREY_BROWN = 'GYBN'
    WHITE_PINK = 'WHPK'
    PINK_BROWN = 'PKBN'
    WHITE_BLUE = 'WHBU'
    BROWN_BLUE = 'BNBU'
    WHITE_RED = 'WHRD'
    BROWN_RED = 'BNRD'
    WHITE_BLACK = 'WHBK'
    BROWN_BLACK = 'BNBK'
    GREY_GREEN = 'GYGN'
    YELLOW_GREY = 'YEGY'
    PINK_GREEN = 'PKGN'
    YELLOW_PINK = 'YEPK'
    GREEN_BLUE = 'GNBU'
    YELLOW_BLUE = 'YEBU'
    GREEN_RED = 'GNRD'
    YELLOW_RED = 'YERD'
    GREEN_BLACK = 'GNBK'
    YELLOW_BLACK = 'YEBK'
    GREY_BLUE = 'GYBU'
    PINK_BLUE = 'PKBU'
    GREY_RED = 'GYRD'
    PINK_RED = 'PKRD'
    GREY_BLACK = 'GYBK'
    PINK_BLACK = 'PKBK'
    BLUE_BLACK = 'BUBK'
    RED_BLACK = 'RDBK'


class Gender(enum.Enum):
    """Connector gender."""

    MALE = 'male'
    FEMALE = 'female'
    NONE = ''


class Connector(BaseModel):
    """Connector definition."""

    type: str = Field(description='Brand name')  # noqa: A003
    gender: Gender = Field(description='Gender')
    color: Color = Field(description='Color')
    pin_names: typing.List[str] = Field(description='Pin names, typically 1, 2, 3, etc.', min_length=1)

    @model_validator(mode='after')
    def check_pin_names(self):
        if len(set(self.pin_names)) != len(self.pin_names):
            raise ValueError('pin_names must be unique')
        return self


class ConnectorInstance(BaseModel):
    """Connector instance."""

    index: int = Field(description='Connector definition index')
    pin_labels: typing.Dict[int, str] = Field(description='Map of pin index -> label')


class Wire(BaseModel):
    """An individual wire within a cable."""

    color: Color = Field(description='The wire insulation color')
    gauge: float = Field(description='The wire gauge in mm^2')


class Cable(BaseModel):
    """Cable definition."""

    type: str = Field(description='Brand name')  # noqa: A003
    bundled: bool = Field(description='Whether the cable wires are bundled into a unit or assembled from individual wires')
    shield: bool = Field(description='Whether or not the cable has a shield')
    color: Color = Field(description='Cable jacket color')
    wires: typing.List[Wire] = Field(description='List of wires', min_length=1)


class CableInstance(BaseModel):
    """Cable instance."""

    index: int = Field(description='Cable definition index')
    length: float = Field(description='Cable length in meters')
    wire_labels: typing.Dict[int, str] = Field(description='Map of wire index -> label')


class HarnessConcept(BaseModel):
    """Wiring harness concept."""
    connectors: typing.Dict[str, ConnectorInstance] = Field(description='List of connectors')
    cables: typing.Dict[str, CableInstance] = Field(description='List of cables')
    connections: typing.List[typing.Dict[str, typing.List[int]]] = Field(
        description='List of connections between connectors and cables. Values must be >= 0 and < pin_count / wirecount.')


class Harness(BaseModel):
    """Wiring harness."""

    connector_defs: typing.List[Connector] = Field(description='Connector definitions', min_length=1)
    cable_defs: typing.List[Cable] = Field(description='Cable definitions', min_length=1)
    connectors: typing.Dict[str, ConnectorInstance] = Field(description='Map of name (e.g. J1, J2, etc.) -> instance')
    cables: typing.Dict[str, CableInstance] = Field(description='Map of name (e.g. W1, W2, etc.) -> instance')
    connections: typing.List[typing.Dict[str, typing.List[int]]] = Field(description='Maps of connector / cable names -> pin / wire indices.')

    @model_validator(mode='after')
    def check_connectors(self):
        for name, connector in self.connectors.items():
            connector_def = self.connector_defs[connector.index]
            for pin_index in connector.pin_labels.keys():
                connector_def.pin_names[pin_index]  # noqa: F841
        return self

    @model_validator(mode='after')
    def check_cables(self):
        for name, cable in self.cables.items():
            cable_def = self.cable_defs[cable.index]
            for wire_index in cable.wire_labels.keys():
                cable_def.wires[wire_index]  # noqa: F841
        return self

    @model_validator(mode='after')
    def check_connections(self):
        for index, connection in enumerate(self.connections):
            for name, items in connection.items():
                if name in self.connectors:
                    connector = self.connectors[name]
                    connector_def = self.connector_defs[connector.index]
                    num_pins = len(connector_def.pin_names)
                    if any(i < 0 or i >= num_pins for i in items):
                        raise ValueError(f'connections[{index}][{name}]: invalid pin index')
                elif name in self.cables:
                    cable = self.cables[name]
                    cable_def = self.cable_defs[cable.index]
                    num_wires = len(cable_def.wires)
                    if any(i < 0 or i >= num_wires for i in items):
                        raise ValueError(f'connections[{index}][{name}]: invalid wire index')
                else:
                    raise ValueError(f'connections[{index}]: "{name}" not found in connectors or cables')
        return self


class ConceptNode(BaseModel):
    """Node in ConceptGraph."""

    component_name: str = Field(min_length=1, description='Component name')
    connector_name: str = Field(min_length=1, description='Connector name  (e.g. J1, J2, etc.) attached to the component')


class ConceptGraph(BaseModel):
    """Connectors the wire harness will join together."""

    nodes: typing.List[ConceptNode] = Field(description='Harness connectors')
    edges: typing.List[typing.Tuple[int, int]] = Field(description='Harness connections, pairs of node indices')

    @model_validator(mode='after')
    def check_graph(self):
        for source_index, target_index in self.edges:
            if not (0 <= source_index < len(self.nodes)):
                raise IndexError('source_index out of range')
            if not (0 <= target_index < len(self.nodes)):
                raise IndexError('target_index out of range')
        return self


def concept_to_mermaid(concept: ConceptGraph) -> str:
    """Create a Mermaid diagram from a concept graph."""
    mermaid_lines = ['graph TD']
    components = {}
    for index, node in enumerate(concept.nodes):
        if node.component_name not in components:
            components[node.component_name] = []
        components[node.component_name].append((index, node.connector_name))
    for component_name, connectors in components.items():
        mermaid_lines.append(f'    subgraph {component_name}')
        for index, connector_name in connectors:
            mermaid_lines.append(f'        node_{index}["{connector_name}"]')
        mermaid_lines.append('    end')
    for edge in concept.edges:
        mermaid_lines.append(f'    node_{edge[0]} --- node_{edge[1]}')
    return '\n'.join(mermaid_lines)


def harness_to_wireviz(harness: Harness) -> str:
    """Create WireViz YAML from a harness definition."""
    wireviz_dict = harness.model_dump(mode='json')
    for item in wireviz_dict['connector_defs']:
        item['subtype'] = item.pop('gender')
        item['pins'] = [int(p) if isinstance(p, str) and p.isdigit() else p for p in item.pop('pin_names')]
    for item in wireviz_dict['cable_defs']:
        wires = item.pop('wires')
        item['colors'] = [wire['color'] for wire in wires]
        item['gauge'] = sorted([wire['gauge'] for wire in wires])[len(wires) // 2]
        if item.pop('bundled'):
            item['category'] = 'bundled'
    for name, connector in wireviz_dict['connectors'].items():
        connector_def_index = connector.pop('index')
        connector_def = wireviz_dict['connector_defs'][connector_def_index]
        pin_labels = connector.pop('pin_labels')
        pinlabels = [''] * len(connector_def['pins'])
        for index, label in pin_labels.items():
            pinlabels[int(index)] = label
        connector['pinlabels'] = pinlabels
        connector['<<'] = connector_def
    for name, cable in wireviz_dict['cables'].items():
        cable_def_index = cable.pop('index')
        cable_def = wireviz_dict['cable_defs'][cable_def_index]
        wire_labels = cable.pop('wire_labels')
        wirelabels = [''] * len(cable_def['colors'])
        for index, label in wire_labels.items():
            wirelabels[int(index)] = label
        cable['wirelabels'] = wirelabels
        cable['<<'] = cable_def
    connections_list = wireviz_dict['connections']
    for index, connection in enumerate(connections_list):
        new_connection = []
        for key, value in connection.items():
            new_connection.append(_resolve_connection_target(key, value, harness))
        connections_list[index] = new_connection
    wireviz_yaml = yaml.safe_dump(wireviz_dict, sort_keys=False)
    return wireviz_yaml.replace("'<<': ", "<<: ")  # HACK: should use a custom YAML dumper...


def wireviz_to_bom(wireviz_yaml: str) -> str:
    """Create a BOM text from a harness definition."""
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = pathlib.Path(temp_dir_str)
        in_path = temp_dir / 'harness.yaml'
        in_path.write_text(wireviz_yaml)
        wireviz_bin = _get_wireviz_cmd()
        command = f'{wireviz_bin} -f t --output-dir {in_path.parent} {in_path}'
        subprocess.run(shlex.split(command), check=True)
        out_path = temp_dir / 'harness.bom.tsv'
        return out_path.read_text()


def wireviz_to_png(wireviz_yaml: str) -> bytes:
    """Create a BOM text from a harness definition."""
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = pathlib.Path(temp_dir_str)
        in_path = temp_dir / 'harness.yaml'
        in_path.write_text(wireviz_yaml)
        wireviz_bin = _get_wireviz_cmd()
        command = f'{wireviz_bin} -f p --output-dir {in_path.parent} {in_path}'
        subprocess.run(shlex.split(command), check=True)
        out_path = temp_dir / 'harness.png'
        return out_path.read_bytes()


def _get_wireviz_cmd() -> str:
    """Get the path to the wireviz executable."""
    sys_wireviz = pathlib.Path(sys.executable).parent / 'wireviz'
    if sys_wireviz.exists():
        return str(sys_wireviz)
    prefix_wireviz = pathlib.Path(sys.prefix) / 'bin' / 'wireviz'
    if prefix_wireviz.exists():
        return str(prefix_wireviz)
    which_wireviz = shutil.which('wireviz')
    if which_wireviz:
        return which_wireviz
    return 'wireviz'


def _resolve_connection_target(key: str, indices: typing.List[int], harness: Harness) -> typing.Dict[str, typing.List[typing.Union[str, int]]]:
    if key in harness.connectors:
        pins = harness.connector_defs[harness.connectors[key].index].pin_names
        return {key: [int(pins[i]) if isinstance(pins[i], str) and pins[i].isdigit() else pins[i] for i in indices]}
    if key in harness.cables:
        return {key: [i + 1 for i in indices]}
    return {key: indices}
