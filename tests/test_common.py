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
                gender=wireviz_mcp.common.Gender.FEMALE,
                color=wireviz_mcp.common.Color.BLACK,
                pin_names=['1', '2', '3', '4', '5', '6', '7', '8', '9'],
            )
        ],
        cable_defs=[
            wireviz_mcp.common.Cable(
                type='YSLY',
                bundled=True,
                shield=False,
                color=wireviz_mcp.common.Color.GREY,
                wires=[
                    wireviz_mcp.common.Wire(color=wireviz_mcp.common.Color.BROWN, gauge=0.5),
                    wireviz_mcp.common.Wire(color=wireviz_mcp.common.Color.BLUE, gauge=0.5),
                    wireviz_mcp.common.Wire(color=wireviz_mcp.common.Color.GREEN, gauge=0.75),
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
                wire_labels={0: 'RX', 1: 'TX', 2: 'GND'},
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


def test_harness_validation_valid(harness):
    """Test that a valid harness object can be created."""
    assert harness is not None


def test_harness_validation_invalid_pin_index(harness):
    """Test that creating a harness with an invalid pin index raises an IndexError."""
    harness_data = harness.model_dump()
    harness_data['connectors']['X1']['pin_labels'][99] = 'extra'

    with pytest.raises(IndexError):
        wireviz_mcp.common.Harness(**harness_data)


def test_harness_validation_invalid_wire_index(harness):
    """Test that creating a harness with an invalid wire index raises an IndexError."""
    harness_data = harness.model_dump()
    harness_data['cables']['W1']['wire_labels'][99] = 'w4'

    with pytest.raises(IndexError):
        wireviz_mcp.common.Harness(**harness_data)


def test_harness_to_wireviz(harness):
    """Test the conversion of a harness to a WireViz YAML string."""
    yaml_str = wireviz_mcp.common.harness_to_wireviz(harness)
    data = yaml.safe_load(yaml_str)

    assert 'connector_defs' in data
    assert 'cable_defs' in data
    assert 'connectors' in data
    assert 'cables' in data
    assert 'connections' in data

    # check connector fields
    assert data['connector_defs'][0]['subtype'] == 'female'
    assert data['connector_defs'][0]['color'] == 'BK'
    assert data['connector_defs'][0]['pins'] == ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    assert len(data['connectors']['X1']['pin_labels']) == 9

    # check cable fields
    assert data['cable_defs'][0]['category'] == 'bundled'
    assert data['cable_defs'][0]['colors'] == ['BN', 'BU', 'GN']
    assert data['cable_defs'][0]['gauge'] == 0.5  # Median of [0.5, 0.5, 0.75]
    assert data['cables']['W1']['length'] == 1.0
    assert len(data['cables']['W1']['wire_labels']) == 3
    assert data['cable_defs'][0]['shield'] is False
    assert data['connections'] == [[{'X1': [2]}, {'W1': [1]}], [{'X1': [3]}, {'W1': [2]}], [{'X1': [5]}, {'W1': [0]}]]


def test_wireviz_to_bom(wireviz_yaml):
    """Test that wireviz_to_bom calls subprocess.run with the correct command."""
    result = wireviz_mcp.common.wireviz_to_bom(wireviz_yaml)
    assert isinstance(result, str)


def test_wireviz_to_png(wireviz_yaml):
    """Test that wireviz_to_png calls subprocess.run with the correct command."""
    # Mock subprocess.run
    result = wireviz_mcp.common.wireviz_to_png(wireviz_yaml)
    assert isinstance(result, bytes)


def test_concept_to_mermaid():
    """Test concept_to_mermaid."""
    concept = wireviz_mcp.common.ConceptGraph(
        nodes=[
            wireviz_mcp.common.ConceptNode(component_name='ComponentA', connector_name='J1'),
            wireviz_mcp.common.ConceptNode(component_name='ComponentB', connector_name='J2'),
            wireviz_mcp.common.ConceptNode(component_name='ComponentA', connector_name='J3'),
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
