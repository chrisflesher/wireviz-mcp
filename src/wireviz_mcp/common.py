"""WireViz model."""

import datetime
import enum
import json
import pathlib
import shlex
import shutil
import subprocess
import sys
import tempfile
import typing

from pydantic import BaseModel, Field, model_validator


class Color(str, enum.Enum):
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

    # Other non-standard colors
    ORANGE = 'OG'
    WHITE_ORANGE = 'WHOG'


class Gauge(str, enum.Enum):
    """Standard AWG sizes."""

    AWG_4_0 = '4/0'
    AWG_3_0 = '3/0'
    AWG_2_0 = '2/0'
    AWG_1_0 = '1/0'
    AWG_1 = '1'
    AWG_2 = '2'
    AWG_4 = '4'
    AWG_6 = '6'
    AWG_8 = '8'
    AWG_10 = '10'
    AWG_12 = '12'
    AWG_14 = '14'
    AWG_16 = '16'
    AWG_18 = '18'
    AWG_20 = '20'
    AWG_21 = '21'
    AWG_22 = '22'
    AWG_24 = '24'
    AWG_26 = '26'
    AWG_28 = '28'
    AWG_30 = '30'

    @property
    def mm2(self) -> float:
        """Return nearest gauge in mm2."""
        areas = {
            '4/0': 120.0,
            '3/0': 95.0,
            '2/0': 70.0,
            '1/0': 55.0,
            '1': 50.0,
            '2': 35.0,
            '4': 25.0,
            '6': 16.0,
            '8': 10.0,
            '10': 6.0,
            '12': 4.0,
            '14': 2.5,
            '16': 1.5,
            '18': 0.75,
            '20': 0.50,
            '21': 0.38,
            '22': 0.34,
            '24': 0.25,
            '26': 0.14,
            '28': 0.08,
            '30': 0.05,
        }
        return areas[self.value]


class GaugeUnit(str, enum.Enum):
    """Length unit of measurement."""

    AWG = 'AWG'
    MM2 = 'mm2'


class Gender(str, enum.Enum):
    """Connector gender."""

    MALE = 'male'
    FEMALE = 'female'
    NONE = ''


class LengthUnit(str, enum.Enum):
    """Length unit of measurement."""

    CENTIMETER = 'cm'
    FOOT = 'ft'
    INCH = 'in'
    METER = 'm'
    MILLIMETER = 'mm'


class Connector(BaseModel):
    """Connector definition."""

    type: str = Field(description='Brand name')  # noqa: A003
    subtype: Gender = Field(description='Gender')
    color: Color = Field(description='Color')
    pins: typing.List[str] = Field(description='Pin names, typically 1, 2, 3, etc.', min_length=1)

    @model_validator(mode='after')
    def check_pins(self):
        """Ensure pin names are unique."""
        if len(set(self.pins)) != len(self.pins):
            raise ValueError('pins must be unique')
        return self


class ConnectorInstance(BaseModel):
    """Connector instance."""

    index: int = Field(description='Connector definition index')
    pin_labels: typing.Mapping[int, str] = Field(description='Map of pin index -> label')


class Wire(BaseModel):
    """An individual wire within a cable."""

    color: Color = Field(description='The wire insulation color')
    gauge: Gauge = Field(description='The wire gauge')


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
    wire_labels: typing.Mapping[int, str] = Field(description='Map of wire index -> label')


class AuthorEntry(BaseModel):
    """Author metadata entry."""

    name: str = Field(description='Author name')
    date: datetime.date = Field(description='Author date (YYYY-MM-DD)')


class RevisionEntry(BaseModel):
    """Revision metadata entry."""

    name: str = Field(description='Author name')
    date: datetime.date = Field(description='Revision date (YYYY-MM-DD)')
    changelog: str = Field(description='Revision changelog summary')


class TemplateConfig(BaseModel):
    """Template options."""

    name: str = Field(default='din-6771', description='WireViz template name')
    sheetsize: str = Field(default='A3', description='Page sheet size (e.g. A4, A3)')


class Metadata(BaseModel):
    """Harness document metadata."""

    title: str = Field(default='Main Harness Assembly', description='Harness assembly title')
    pn: typing.Optional[str] = Field(default=None, description='Part number')
    company: typing.Optional[str] = Field(default=None, description='Company name')
    authors: typing.Mapping[str, AuthorEntry] = Field(default_factory=dict, description='Dictionary of authors/roles')
    revisions: typing.Mapping[str, RevisionEntry] = Field(default_factory=dict, description='Dictionary of revisions')
    template: TemplateConfig = Field(default_factory=TemplateConfig, description='Template settings')


class Harness(BaseModel):
    """Wiring harness."""

    connector_defs: typing.List[Connector] = Field(description='Connector definitions', min_length=1)
    cable_defs: typing.List[Cable] = Field(description='Cable definitions', min_length=1)
    connectors: typing.Mapping[str, ConnectorInstance] = Field(description='Map of name (e.g. J1, J2, etc.) -> instance')
    cables: typing.Mapping[str, CableInstance] = Field(description='Map of name (e.g. W1, W2, etc.) -> instance')
    connections: typing.List[typing.Mapping[str, typing.List[int]]] = Field(description='Maps of connector / cable names -> pin / wire indices.')
    metadata: Metadata = Field(default_factory=Metadata, description='Harness metadata')

    @model_validator(mode='after')
    def check_connectors(self):
        """Ensure connector instances are valid."""
        for name, connector in self.connectors.items():
            connector_def = self.connector_defs[connector.index]
            for pin_index in connector.pin_labels.keys():
                if not (0 <= pin_index < len(connector_def.pins)):
                    raise ValueError(f'connectors[{name}]: invalid pin index {pin_index}')
        return self

    @model_validator(mode='after')
    def check_cables(self):
        """Ensure cable instances are valid."""
        for name, cable in self.cables.items():
            cable_def = self.cable_defs[cable.index]
            for wire_index in cable.wire_labels.keys():
                if not (0 <= wire_index < len(cable_def.wires)):
                    raise ValueError(f'cables[{name}]: invalid wire index {wire_index}')
        return self

    @model_validator(mode='after')
    def check_connections(self):
        """Ensure connection instances are valid."""
        for index, connection in enumerate(self.connections):
            for name, items in connection.items():
                if name in self.connectors:
                    connector = self.connectors[name]
                    connector_def = self.connector_defs[connector.index]
                    num_pins = len(connector_def.pins)
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


class HarnessConceptNode(BaseModel):
    """Node in HarnessConcept graph."""

    component_name: str = Field(min_length=1, description='Component name')
    connector_name: str = Field(min_length=1, description='Connector name  (e.g. J1, J2, etc.) attached to the component')


class HarnessConcept(BaseModel):
    """Graph of connectors the wire harness will join together."""

    nodes: typing.List[HarnessConceptNode] = Field(description='Harness connectors')
    edges: typing.List[typing.Tuple[int, int]] = Field(description='Harness connections, pairs of node indices')

    @model_validator(mode='after')
    def check_graph(self):
        """Ensure graph is valid."""
        for source_index, target_index in self.edges:
            if not (0 <= source_index < len(self.nodes)):
                raise IndexError('source_index out of range')
            if not (0 <= target_index < len(self.nodes)):
                raise IndexError('target_index out of range')
        return self


def concept_to_mermaid(concept: HarnessConcept) -> str:
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


def harness_to_wireviz(
    harness: Harness,
    gauge_unit: GaugeUnit = GaugeUnit.AWG,
    length_unit: LengthUnit = LengthUnit.METER,
) -> typing.Mapping[str, typing.Any]:
    """Create WireViz JSON dict structure from a harness definition."""
    harness_dict = harness.model_dump(mode='json')
    wireviz_connectors = {
        name: _build_wireviz_connector(conn, harness.connector_defs[conn.index])
        for name, conn in harness.connectors.items()
    }
    wireviz_cables = {
        name: _build_wireviz_cable(cbl, harness.cable_defs[cbl.index], gauge_unit, length_unit)
        for name, cbl in harness.cables.items()
    }
    wireviz_connections = [
        _build_wireviz_connection(conn, harness) for conn in harness.connections
    ]
    return {
        'connectors': wireviz_connectors,
        'cables': wireviz_cables,
        'connections': wireviz_connections,
        'metadata': harness_dict.get('metadata', {}),
    }


def wireviz_to_html(wireviz_input: typing.Union[str, typing.Mapping[str, typing.Any]]) -> str:
    """Create an HTML document string from a WireViz definition (JSON or YAML string/dict)."""
    if isinstance(wireviz_input, (dict, typing.Mapping)):
        content = json.dumps(dict(wireviz_input), indent=2)
    else:
        content = wireviz_input

    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = pathlib.Path(temp_dir_str)
        in_path = temp_dir / 'harness.json'
        in_path.write_text(content)
        wireviz_bin = _get_wireviz_cmd()
        command = f'{wireviz_bin} -f h --output-dir {in_path.parent} {in_path}'
        res = subprocess.run(shlex.split(command), capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f'WireViz CLI error:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}')

        out_html = temp_dir / 'harness.html'
        if out_html.exists():
            return out_html.read_text()
        raise RuntimeError('WireViz did not produce expected HTML output')


def _build_wireviz_cable(
    instance: CableInstance,
    cdef: Cable,
    gauge_unit: GaugeUnit,
    length_unit: LengthUnit,
) -> typing.Mapping[str, typing.Any]:
    colors = [w.color for w in cdef.wires]
    gauges = sorted([_build_wireviz_gauge_str(w.gauge, gauge_unit) for w in cdef.wires])
    median_gauge = gauges[len(gauges) // 2]
    wirelabels = [''] * len(colors)
    for idx, label in instance.wire_labels.items():
        wirelabels[idx] = label
    cable_dict: typing.Dict[str, typing.Any] = {
        'type': cdef.type,
        'color': cdef.color,
        'colors': colors,
        'gauge': median_gauge,
        'shield': cdef.shield,
        'wirelabels': wirelabels,
        'length': _build_wireviz_length_str(instance.length, length_unit),
    }
    if cdef.bundled:
        cable_dict['category'] = 'bundled'
    return cable_dict


def _build_wireviz_connector(instance: ConnectorInstance, cdef: Connector) -> typing.Mapping[str, typing.Any]:
    raw_pins = cdef.pins
    pins = [int(p) if isinstance(p, str) and p.isdigit() else p for p in raw_pins]
    pinlabels = [''] * len(pins)
    for idx, label in instance.pin_labels.items():
        pinlabels[idx] = label
    return {
        'type': cdef.type,
        'subtype': cdef.subtype,
        'color': cdef.color,
        'pins': pins,
        'pinlabels': pinlabels,
    }


def _build_wireviz_connection(
    connection: typing.Mapping[str, typing.List[int]],
    harness: Harness,
) -> typing.List[typing.Mapping[str, typing.List[typing.Union[str, int]]]]:
    conn_keys = list(connection.keys())
    cables_keys = [k for k in conn_keys if k in harness.cables]
    connectors_keys = [k for k in conn_keys if k in harness.connectors]
    other_keys = [k for k in conn_keys if k not in harness.cables and k not in harness.connectors]
    ordered_keys = []
    if connectors_keys and cables_keys:
        ordered_keys.append(connectors_keys[0])
        ordered_keys.extend(cables_keys)
        ordered_keys.extend(connectors_keys[1:])
        ordered_keys.extend(other_keys)
    else:
        ordered_keys = conn_keys
    result = []
    for key in ordered_keys:
        indices = connection[key]
        if key in harness.connectors:
            pins = harness.connector_defs[harness.connectors[key].index].pins
            resolved = [int(pins[i]) if isinstance(pins[i], str) and pins[i].isdigit() else pins[i] for i in indices]
            result.append({key: resolved})
        elif key in harness.cables:
            result.append({key: [i + 1 for i in indices]})
        else:
            result.append({key: indices})
    return result


def _build_wireviz_gauge_str(gauge: Gauge, unit: GaugeUnit) -> str:
    """Convert a gauge to a text string."""
    if unit == GaugeUnit.AWG:
        gauge_str = f'{gauge.value}'
    elif unit == GaugeUnit.MM2:
        gauge_str = f'{gauge.mm2}'
    else:
        raise ValueError(f'Unknown unit: {unit}')
    return f'{gauge_str} {unit.value}'


def _build_wireviz_length_str(length: float, unit: LengthUnit) -> str:
    """Convert a length in meters to a text string."""
    if unit == LengthUnit.CENTIMETER:
        length_str = f'{round(length * 100):d}'
    elif unit == LengthUnit.FOOT:
        length_str = f'{round(length * 3.28084):d}'
    elif unit == LengthUnit.INCH:
        length_str = f'{round(length * 39.3701):d}'
    elif unit == LengthUnit.METER:
        length_str = f'{length:g}'
    elif unit == LengthUnit.MILLIMETER:
        length_str = f'{round(length * 1000):d}'
    else:
        raise ValueError(f'Unknown unit: {unit}')
    return f'{length_str} {unit.value}'


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
