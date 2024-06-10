import dash
from dash import html
from dash import dcc
from dash import dash_table
import dash_cytoscape as cyto
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle
import pandas as pd


# Sample Data for DataTable
data = {
    "Id": ["node1", "node2", "edge1"],
    "Label": ["Node 1", "Node 2", "Edge from Node 1 to Node 2"],
    "Type": ["Node", "Node", "Edge"]
}
df = pd.DataFrame(data)

# Initialize the Dash app
app = dash.Dash(__name__)


# Styles are defined in assets/style.css
app.layout = html.Div(
    className="container",
    children=[
        PanelGroup(
            id="panel-group",
            children=[

                Panel(
                    id="panel-2",
                    children=[
                        PanelGroup(
                            id="panel-group-2",
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
                                    style={'width': '100%', 'height': '100%', 'border': '1px solid black'},
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
                                    style={'width': '100%', 'height': '100%', 'border': '1px solid black'},
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
                    style={'width': '100%', 'height': '100%', 'border': '1px solid black'},
                    defaultSizePercentage=30,
                    minSizePercentage=20,
                    collapsible=False,
                    collapsedSizePercentage=0
                )
            ],
            direction="vertical",
        )
    ],
)

if __name__ == '__main__':
    app.run_server(debug=True, dev_tools_ui=False)

