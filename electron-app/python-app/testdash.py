import uuid

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

app = dash.Dash(__name__, external_stylesheets=[
])

app.layout = html.Div(
    children=[
        dcc.Store(id='session-state', storage_type='session'),
        dcc.Store(id='session-id', storage_type='session'),
        html.Button('Initialize', id='initial-load'),
        html.Div(id="output")
    ]
)


@app.callback(
    Output('session-state', 'data'),
    Output('session-id', 'data'),
    Input('initial-load', 'n_clicks')
)
def initialize_session_state(n_clicks):
    if n_clicks is None:
        raise PreventUpdate

    session_id = str(uuid.uuid4())  # Generate a unique session ID
    session_data = {'initialized': True, 'value': 42}
    print(f"Session initialized with ID: {session_id}")
    return session_data, session_id


@app.callback(
    Output('output', 'children'),
    Input('session-state', 'modified_timestamp'),
    State('session-state', 'data'),
    State('session-id', 'data')
)
def update_output(ts, session_data, session_id):
    print(f"Updating output with session ID: {session_id} and data: {session_data}")
    if ts is None:
        raise PreventUpdate
    if session_data and session_id:
        return f"Session {session_id} initialized: {session_data['initialized']} with value: {session_data['value']}"
    return "Session not initialized"


if __name__ == '__main__':
    app.run_server(debug=True)