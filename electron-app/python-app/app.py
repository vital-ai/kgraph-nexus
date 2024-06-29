import logging
import time
import os
import sys


start_time = time.time()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for PyInstaller onefile """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


bootstrap_icons_path = resource_path('assets/bootstrap-icons.min.css')
bootstrap_css_path = resource_path('assets/bootstrap.min.css')


logger.info("App Before Imports in %s seconds", time.time() - start_time)

import flask
from flask import request, jsonify
import dash
from dash import html
from dash import dcc
from dash import dash_table
import dash_cytoscape as cyto
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

logger.info("App Imports in %s seconds", time.time() - start_time)

# this didn't work
# import warnings
# warnings.filterwarnings("ignore", category=UserWarning, message="This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.")

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Sample Data for DataTable
data = {
    "Id": ["node1", "node2", "edge1"],
    "Label": ["Node 1", "Node 2", "Edge from Node 1 to Node 2"],
    "Type": ["Node", "Node", "Edge"]
}
df = pd.DataFrame(data)

logger.info("App Dataframe in %s seconds", time.time() - start_time)


search_options = [
    {"label": "IPhone", "value": "IPhone"},
    {"label": "Samsung Phone", "value": "Samsung Phone"},
    {"label": "Google Pixel", "value": "Google Pixel"},
    {"label": "Phone Case", "value": "Phone Case"},
]

layout_options = [
    {"label": "Layout 1", "value": "layout-1"},
    {"label": "Layout 2", "value": "layout-2"},
    {"label": "Layout 3", "value": "layout-3"}
]

# dbc.ButtonGroup(
# [
#    dbc.Button("Layout 1", id="layout-1", className="btn btn-primary"),
#    dbc.Button("Layout 2", id="layout-2", className="btn btn-primary"),
#    dbc.Button("Layout 3", id="layout-3", className="btn btn-primary"),
#    dbc.Button("Layout 4", id="layout-4", className="btn btn-primary"),
#        ],
#        size="md"
#    ),


# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[
    # dbc.themes.BOOTSTRAP,
    bootstrap_css_path,
    bootstrap_icons_path,
    # "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.4.1/font/bootstrap-icons.min.css"
], title="Knowledge Graph Nexus")


# Styles are defined in assets/style.css
app.layout = html.Div(
    className="container",
    children=[
        PanelGroup(
            id="panel-group",
            children=[
                Panel(
                    id="panel-1",
                    style={'position': 'relative', 'zIndex': '1'},
                    children=[
                        dbc.Row(
                            [
                                dbc.Col(
html.Div(
                    [
                                    dbc.ButtonGroup(
                                        [
                                            dbc.Button(html.I(className="bi bi-save"), id="btn-save", title="Export",
                                                       className="btn btn-primary"),
                                            dbc.Button(html.I(className="bi bi-save rotate-180"), id="btn-load",
                                                       title="Import", className="btn btn-primary"),
                                            dbc.Button(html.I(className="bi bi-x-circle"), id="btn-new",
                                                       title="Clear Graph", className="btn btn-primary")
                                        ],
                                        size="md"
                                    )
                                ],


),                                 width="auto"
                                ),
dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.Input(id="search-input", placeholder="Search..."),
                        dbc.Button("Search", id="search-button", n_clicks=0, className="btn btn-primary"),
                        html.Div([
                            dbc.Switch(
                                id="search-type-toggle",
                                value=True,
                                className="ms-2"  # Margin start (left margin), adjust as needed
                            ),
                            html.Span(id="toggle-label", children="Service", className="ms-2 align-middle")
                        ], style={'display': 'flex', 'alignItems': 'center'})  # Ensures label and switch are aligned

                    ],
                    size="md",
                    className="search-bar"
                ),
                width="6",
            ),
                            ],
                            align="center",
                            className="mb-4"
                        ),
                        dbc.Modal(
                            [
                                dbc.ModalHeader(dbc.ModalTitle("Search Results")),
                                dbc.ModalBody(
                dash_table.DataTable(
                    id='search-results-table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=[],  # Initially empty
                    style_table={'height': '300px', 'overflowY': 'auto'},
                    style_cell={'textAlign': 'left'},
                )
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
            ),
        ],
        id="modal",
        is_open=False,
        size="lg",  # you can use "sm", "lg", "xl" for different sizes
    )
                    ],
                    defaultSizePercentage=10,
                    minSizePercentage=10,
                    collapsible=False
                ),
                PanelResizeHandle(html.Div(id="top-resize-bar", className="resize-handle-vertical")),

                Panel(
                    id="panel-2",
                    style={'position': 'relative', 'zIndex': '1'},
                    children=[
                        PanelGroup(
                            id="panel-group-2",
                            style={'position': 'relative', 'zIndex': '1'},
                            children=[
                                Panel(
                                    id="panel-graph",
                                    children=[
                                        cyto.Cytoscape(
                                            id='cytoscape-graph',
                                            layout={'name': 'preset'},
                                            style={'width': '100%', 'height': '100%'},
                                            elements=[
                                                {'data': {'id': 'node1', 'label': 'Node 1'}, 'position': {'x': 75, 'y': 75}},
                                                {'data': {'id': 'node2', 'label': 'Node 2'}, 'position': {'x': 200, 'y': 200}},
                                                {'data': {'id': 'edge1', 'source': 'node1', 'target': 'node2'}}
                                            ]
                                        )
                                    ],
                                    style={'position': 'relative', 'zIndex': '1', 'width': '100%', 'height': '100%', 'border': '1px solid black'},
                                    defaultSizePercentage=50,
                                    minSizePercentage=10,
                                    collapsible=False,
                                    collapsedSizePercentage=0
                                ),
                                PanelResizeHandle(
                                    html.Div(className="resize-handle-horizontal")
                                ),
                                Panel(
                                    id="panel-tabs",
                                    children=[
                                        dcc.Tabs(id='tabs', children=[
                                            dcc.Tab(label='Palette', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                                                html.Div("Drag and drop nodes and edges here.")
                                            ]),
                                            dcc.Tab(label='Query', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                                                html.Div("Query the database.")
                                            ]),
                                            dcc.Tab(label='Selection', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                                                html.Div("Show details of selected items.")
                                            ]),
                                            dcc.Tab(label='Generate', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                                                html.Div("Generate graph elements from Documents.")
                                            ]),
                                            dcc.Tab(label='Connection', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                                                html.Div("Connect to a database.")
                                            ])
                                        ])
                                    ],
                                    style={'position': 'relative', 'zIndex': '1', 'width': '100%', 'height': '100%', 'border': '1px solid black'},
                                    defaultSizePercentage=50,
                                    minSizePercentage=10,
                                    collapsible=False,
                                    collapsedSizePercentage=0
                                )
                            ],
                            direction="horizontal",
                        )
                    ],
                    minSizePercentage=50,
                ),
                PanelResizeHandle(html.Div(className="resize-handle-vertical")),
                Panel(
                    id='panel-data-table',
                    children=[
                        dash_table.DataTable(
                            id='data-table',
                            columns=[{"name": i, "id": i} for i in df.columns],
                            data=df.to_dict('records'),
                            style_table={'height': '100%', 'overflowY': 'auto'}
                        )
                    ],
                    style={'position': 'relative', 'zIndex': '1', 'width': '100%', 'height': '100%', 'border': '1px solid black'},
                    defaultSizePercentage=30,
                    minSizePercentage=20,
                    collapsible=False,
                    collapsedSizePercentage=0
                )
            ],
            direction="vertical",
        ),
        html.Div(id="output")
    ],
)


# Callback to toggle the modal and update the table data
@app.callback(
    Output("modal", "is_open"),
    Output("search-results-table", "data"),
    [Input("search-button", "n_clicks"), Input("close-modal", "n_clicks")],
    [dash.dependencies.State("search-input", "value"), dash.dependencies.State("modal", "is_open")],
)
def toggle_modal(n_search, n_close, search_value, is_open):
    if n_search or n_close:
        if n_search and not is_open:
            # Ensure search_value is a string
            if not isinstance(search_value, str):
                search_value = ""
            try:
                # Filter the data based on the search value
                filtered_data = df[df['Label'].str.contains(search_value, case=False, na=False)].to_dict('records')
                return not is_open, filtered_data
            except Exception as e:
                logger.info(f"Error filtering data: {e}")
                return not is_open, []
        return not is_open, []
    return is_open, []


@app.callback(
    Output("toggle-label", "children"),
    Input("search-type-toggle", "value")
)
def update_label(is_service):
    return "Service" if is_service else "Local"


@app.server.route('/health', methods=['GET'])
def health_check():
    return flask.jsonify({'status': 'ok'})


# handle adding and removing windows with each window having
# an in memory graph
@app.server.route('/graph', methods=['POST'])
def handle_graph():
    data = request.get_json()
    logging.info(f"Received at /graph: {data}")
    return jsonify({'status': 'ok'})


@app.server.route('/query', methods=['POST'])
def handle_query():
    data = request.get_json()
    logging.info(f"Received at /query: {data}")
    return jsonify({'status': 'ok'})


@app.server.route('/graph-query', methods=['POST'])
def handle_graph_query():
    data = request.get_json()
    logging.info(f"Received at /graph-query: {data}")
    return jsonify({'status': 'ok'})


@app.server.route('/kgraphgen', methods=['POST'])
def handle_kgraphgen():
    data = request.get_json()
    logging.info(f"Received at /kgraphgen: {data}")
    return jsonify({'status': 'ok'})


@app.server.route('/connection', methods=['POST'])
def handle_connection():
    data = request.get_json()
    logging.info(f"Received at /connection: {data}")
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    logger.info("Starting app")
    logger.info("App runtime started in %s seconds", time.time() - start_time)

    port = 9000
    app.run_server(port=port, debug=False, dev_tools_ui=False)

