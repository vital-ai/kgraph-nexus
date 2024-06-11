import dash
from dash import html
from dash import dcc
from dash import dash_table
import dash_cytoscape as cyto
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

# Sample Data for DataTable
data = {
    "Id": ["node1", "node2", "edge1"],
    "Label": ["Node 1", "Node 2", "Edge from Node 1 to Node 2"],
    "Type": ["Node", "Node", "Edge"]
}
df = pd.DataFrame(data)

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

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[
    dbc.themes.BOOTSTRAP,
    "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.4.1/font/bootstrap-icons.min.css"
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
                                            dbc.Button(html.I(className="bi bi-save"), id="btn-save", title="Save",
                                                       className="btn btn-primary"),
                                            dbc.Button(html.I(className="bi bi-folder2-open"), id="btn-load",
                                                       title="Load", className="btn btn-primary"),
                                            dbc.Button(html.I(className="bi bi-file-earmark"), id="btn-new",
                                                       title="New", className="btn btn-primary")
                                        ],
                                        size="lg"
                                    ),
dbc.ButtonGroup(
                            [
                                dbc.Button("Layout 1", id="layout-1", className="btn btn-primary"),
                                dbc.Button("Layout 2", id="layout-2", className="btn btn-primary"),
                                dbc.Button("Layout 3", id="layout-3", className="btn btn-primary"),
                                dbc.Button("Layout 4", id="layout-4", className="btn btn-primary"),
                            ],
                            size="lg"
                        ),

                                ],


),                                 width="auto"
                                ),
dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.Input(id="search-input", placeholder="Search..."),
                        dbc.Button("Search", id="search-button", n_clicks=0, className="btn btn-primary"),
                    ],
                    size="lg",
                    className="search-bar"
                ),
                width="auto",
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
                    defaultSizePercentage=20,
                    minSizePercentage=15,
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
                                    defaultSizePercentage=70,
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
                                            dcc.Tab(label='Palette', children=[
                                                html.Div("Drag and drop nodes and edges here.")
                                            ]),
                                            dcc.Tab(label='Query', children=[
                                                html.Div("Query the database.")
                                            ]),
                                            dcc.Tab(label='Selection', children=[
                                                html.Div("Show details of selected items.")
                                            ]),
                                            dcc.Tab(label='Connection', children=[
                                                html.Div("Connect to a database.")
                                            ])
                                        ])
                                    ],
                                    style={'position': 'relative', 'zIndex': '1', 'width': '100%', 'height': '100%', 'border': '1px solid black'},
                                    defaultSizePercentage=30,
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
                print(f"Error filtering data: {e}")
                return not is_open, []
        return not is_open, []
    return is_open, []


if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)
