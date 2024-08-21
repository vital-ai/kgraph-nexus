import dash_cytoscape as cyto
import dash_bootstrap_components as dbc
from dash import dcc, html


def create_graph_list():
    return [
        cyto.Cytoscape(
            id='cytoscape-graph',
            layout={'name': 'preset'},
            style={'width': '100%', 'height': '100%'},
            elements=[
                {'data': {'id': 'node1', 'label': 'Node 1'}, 'position': {'x': 75, 'y': 75}},
                {'data': {'id': 'node2', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
                {'data': {'id': 'edge1', 'source': 'node1', 'target': 'node2'}}
            ],
            boxSelectionEnabled=True,
            userPanningEnabled=True,
            userZoomingEnabled=True
        )
    ]
