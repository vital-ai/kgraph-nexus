from dash import html, dcc
import dash_bootstrap_components as dbc


def create_header():
    return dbc.Row(
        [
            dbc.Col(
                html.Div(
                    dbc.ButtonGroup(
                        [
                            dbc.Button(html.I(className="bi bi-save icon-vertical"), id="btn-save", title="Export", className="btn btn-primary"),
                            # dbc.Button(html.I(className="bi bi-save rotate-180 icon-vertical"), id="btn-load", title="Import", className="btn btn-primary"),
                            dcc.Upload(
                                id='upload-data',
                                children=dbc.Button(html.I(className="bi bi-save rotate-180 icon-vertical"),
                                                    id="btn-load", title="Import", className="btn btn-primary"),
                                style={
                                    'display': 'inline-block',
                                    'cursor': 'pointer'
                                },
                                multiple=False
                            ),
                            dbc.Button(html.I(className="bi bi-x-circle icon-vertical"), id="btn-new", title="Clear Graph", className="btn btn-primary"),
                            dbc.Button(html.I(className="bi bi--crosshair2 icon-vertical"), id="btn-recenter", title="Recenter", className="btn btn-primary"),
                            dcc.Download(id="download-data-file")
                        ],
                        size="md"
                    )
                ),
                width="auto"
            ),
            dbc.Col(
                dbc.InputGroup(
                    [
                        dbc.Input(id="search-input", placeholder="Search..."),
                        dbc.Button("Search", id="search-button", n_clicks=0, className="btn btn-primary"),
                        html.Div(
                            [
                                dbc.Switch(id="search-type-toggle", value=True, className="ms-2"),
                                html.Span(id="toggle-label", children="Service", className="ms-2 align-middle", style={'width': '60px'})
                            ],
                            style={'display': 'flex', 'alignItems': 'center'}
                        )
                    ],
                    size="md",
                    className="search-bar"
                ),
                width="6"
            )
        ],
        align="center",
        className="mb-4"
    )


# dbc.ButtonGroup(
# [
#    dbc.Button("Layout 1", id="layout-1", className="btn btn-primary"),
#    dbc.Button("Layout 2", id="layout-2", className="btn btn-primary"),
#    dbc.Button("Layout 3", id="layout-3", className="btn btn-primary"),
#    dbc.Button("Layout 4", id="layout-4", className="btn btn-primary"),
#        ],
#        size="md"
#    ),
