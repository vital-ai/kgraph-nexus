from dash import html
import dash_bootstrap_components as dbc
from dash import dash_table


def create_modal(df):
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Search Results")),
            dbc.ModalBody(
                dash_table.DataTable(
                    id='search-results-table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=[],  # Initially empty
                    style_table={'height': '300px', 'overflowY': 'auto'},
                    style_cell={'textAlign': 'left'}
                )
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-modal", className="ms-auto", n_clicks=0)
            )
        ],
        id="modal",
        is_open=False,
        # backdrop='static', # keep modal open
        size="lg"
    )
