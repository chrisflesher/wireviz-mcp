"""Tests for the common module."""

import pytest
import yaml

import wireviz_mcp.common


@pytest.fixture
def harness():
    """Return a valid harness object."""
    return wireviz_mcp.common.Harness(
        connector_defs=[
            wireviz_mcp.common.Connector(
                type='D-Sub',
                subtype=wireviz_mcp.common.Gender.FEMALE,
                color=wireviz_mcp.common.Color.BLACK,
                pins=['1', '2', '3', '4', '5', '6', '7', '8', '9'],
            )
        ],
        cable_defs=[
            wireviz_mcp.common.Cable(
                type='YSLY',
                bundled=True,
                shield=False,
                color=wireviz_mcp.common.Color.GREY,
                wires=[
                    wireviz_mcp.common.Wire(color=wireviz_mcp.common.Color.BROWN, gauge=wireviz_mcp.common.Gauge.AWG_20),
                    wireviz_mcp.common.Wire(color=wireviz_mcp.common.Color.BLUE, gauge=wireviz_mcp.common.Gauge.AWG_20),
                    wireviz_mcp.common.Wire(color=wireviz_mcp.common.Color.GREEN, gauge=wireviz_mcp.common.Gauge.AWG_18),
                ],
            )
        ],
        connectors={
            'X1': wireviz_mcp.common.ConnectorInstance(
                index=0,
                pin_labels={0: 'DCD', 1: 'RX', 2: 'TX', 3: 'DTR', 4: 'GND', 5: 'DSR', 6: 'RTS', 7: 'CTS', 8: 'RI'},
            )
        },
        cables={
            'W1': wireviz_mcp.common.CableInstance(
                index=0,
                length=1.0,
            )
        },
        connections=[
            {'X1': [2], 'W1': [1]},
            {'X1': [3], 'W1': [2]},
            {'X1': [5], 'W1': [0]},
        ],
    )


@pytest.fixture
def wireviz_yaml():
    """A simple, valid WireViz YAML string for testing."""
    return """
connectors:
  X1:
    type: Molex Micro-Fit
    pins: [1, 2]

cables:
  W1:
    gauge: 0.34 mm2
    colors: [BK, RD]

connections:
  - - X1: [1, 2]
    - W1: [1, 2]
"""


def test_connector_duplicate_pin_names():
    """Test that creating a connector with duplicate pin names raises a ValueError."""
    with pytest.raises(ValueError, match='pins must be unique'):
        wireviz_mcp.common.Connector(
            type='D-Sub',
            subtype=wireviz_mcp.common.Gender.FEMALE,
            color=wireviz_mcp.common.Color.BLACK,
            pins=['1', '1', '2'],
        )


def test_harness_validation_valid(harness):
    """Test that a valid harness object can be created."""
    assert harness is not None


def test_harness_validation_invalid_pin_index(harness):
    """Test that creating a harness with an invalid pin index raises a ValueError."""
    harness_data = harness.model_dump()
    harness_data['connectors']['X1']['pin_labels'][99] = 'extra'

    with pytest.raises(ValueError, match='invalid pin index'):
        wireviz_mcp.common.Harness(**harness_data)


def test_harness_validation_invalid_cable_index(harness):
    """Test that creating a harness with an invalid cable index raises a ValueError."""
    harness_data = harness.model_dump()
    harness_data['cables']['W1']['index'] = 99

    with pytest.raises(ValueError, match='invalid cable index'):
        wireviz_mcp.common.Harness(**harness_data)


def test_harness_validation_out_of_range_connection_index(harness):
    """Test that creating a harness with an out-of-range connection pin index raises a ValueError."""
    harness_data = harness.model_dump()
    harness_data['connections'].append({'X1': [99]})

    with pytest.raises(ValueError, match='invalid pin index'):
        wireviz_mcp.common.Harness(**harness_data)


def test_harness_to_wireviz(harness):
    """Test the conversion of a harness to WireViz JSON dictionary."""
    data = wireviz_mcp.common.harness_to_wireviz(harness)

    assert 'connectors' in data
    assert 'cables' in data
    assert 'connections' in data
    assert 'metadata' in data

    # check connector fields
    assert data['connectors']['X1']['subtype'] == 'female'
    assert data['connectors']['X1']['color'] == 'BK'
    assert data['connectors']['X1']['pins'] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert len(data['connectors']['X1']['pinlabels']) == 9

    # check cable fields
    assert data['cables']['W1']['category'] == 'bundled'
    assert data['cables']['W1']['colors'] == ['BN', 'BU', 'GN']
    assert data['cables']['W1']['gauge'] == '20 AWG'
    assert data['cables']['W1']['length'] == '1 m'
    assert data['cables']['W1']['wirelabels'] == ['20 AWG BN', '20 AWG BU', '18 AWG GN']
    assert data['cables']['W1']['shield'] is False
    assert data['connections'] == [[{'X1': [3]}, {'W1': [2]}], [{'X1': [4]}, {'W1': [3]}], [{'X1': [6]}, {'W1': [1]}]]


def test_wireviz_to_html(harness):
    """Test that wireviz_to_html compiles wireviz definition without error."""
    json_dict = wireviz_mcp.common.harness_to_wireviz(harness)
    result = wireviz_mcp.common.wireviz_to_html(json_dict)
    assert isinstance(result, str)
    assert '<html>' in result.lower() or '<!doctype html>' in result.lower()


def test_concept_to_mermaid():
    """Test concept_to_mermaid."""
    concept = wireviz_mcp.common.HarnessConcept(
        nodes=[
            wireviz_mcp.common.HarnessConceptNode(component_name='ComponentA', connector_name='J1'),
            wireviz_mcp.common.HarnessConceptNode(component_name='ComponentB', connector_name='J2'),
            wireviz_mcp.common.HarnessConceptNode(component_name='ComponentA', connector_name='J3'),
        ],
        edges=[(0, 1), (2, 1)],
    )
    mermaid_str = wireviz_mcp.common.concept_to_mermaid(concept)
    expected_str = '''graph TD
    subgraph ComponentA
        node_0["J1"]
        node_2["J3"]
    end
    subgraph ComponentB
        node_1["J2"]
    end
    node_0 --- node_1
    node_2 --- node_1
'''
    assert mermaid_str.strip() == expected_str.strip()


def test_harness_to_wireviz_custom_units(harness):
    """Test the conversion of a harness to WireViz dict with custom units."""
    data = wireviz_mcp.common.harness_to_wireviz(
        harness,
        gauge_unit=wireviz_mcp.common.GaugeUnit.MM2,
        length_unit=wireviz_mcp.common.LengthUnit.CENTIMETER,
    )
    assert data['cables']['W1']['gauge'] == '0.5 mm2'
    assert data['cables']['W1']['length'] == '100 cm'
    assert data['cables']['W1']['wirelabels'] == ['0.5 mm2 BN', '0.5 mm2 BU', '0.75 mm2 GN']


