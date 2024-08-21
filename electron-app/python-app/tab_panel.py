from dash import dcc, html
import dash_bootstrap_components as dbc


def create_tabs():
    return dcc.Tabs(
        id='tabs',
        children=[
            dcc.Tab(label='Chat', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                html.Div("Interact with KG Agent.")
            ]),
            dcc.Tab(label='Graph', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                html.Div("Palette. Add nodes and edges.  Edit visual styles.  Layout.")
            ]),
            dcc.Tab(label='Explore', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                html.Div("Explore the database.")
            ]),
            dcc.Tab(label='Selection', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                html.Div("Show details of selected items.")
            ]),
            dcc.Tab(label='Generate', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                html.Div("Generate graph elements from Document."),

                dcc.Upload(
                    id='upload-document',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.Button('Select File')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    multiple=False
                ),
                html.Div(id='file-name', style={'margin-top': '10px'}),
                dbc.Button('Upload File', id='upload-button', className='btn btn-primary', n_clicks=0),
                html.Div(id='output-document-upload'),
                dcc.Store(id='stored-file', data={'contents': None, 'filename': None, 'last_modified': None})

            ]),
            dcc.Tab(label='Connection', selected_style={"fontSize": "12px"}, style={"fontSize": "12px"}, children=[
                html.Div("Connect to a database.  Connect to Agent.")
            ])
        ]
    )
