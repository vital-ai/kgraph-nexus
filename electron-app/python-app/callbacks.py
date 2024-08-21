import base64
import io
import json
import logging
import uuid
from datetime import datetime
import flask
from dash import dcc, html, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from flask import request, jsonify
import pandas as pd
import dash
from flask_socketio import SocketIO, emit

logger = logging.getLogger(__name__)

# Sample Data for DataTable
data = {
    "Id": ["node1", "node2", "edge1"],
    "Label": ["Node 1", "Node 2", "Edge from Node 1 to Node 2"],
    "Type": ["Node", "Node", "Edge"]
}
df = pd.DataFrame(data)


def register_callbacks(app):
    @app.callback(
        State("socketio", "socketId"),
        Input("socketio", "data-notification"),
        prevent_initial_call=True,
    )
    def display_notification(socket_id, message):
        print(f"Message({socket_id}): {message}")

    @app.callback(
        # Output('output', 'children'),
        [Input('ws', 'message')]
    )
    def update_output(message):
        print(f"Received: {message}")
        # return html.Div(f"Received message: {message['data']}")

    # pass nclicks in reply to force update each time
    @app.callback(
        Output('cytoscape-graph', 'layout'),
        Input('btn-recenter', 'n_clicks')
    )
    def recenter_graph(n_clicks):
        if n_clicks is None:
            raise dash.exceptions.PreventUpdate
        return {'name': 'preset', 'fit': True, 'padding': 10, 'key': str(n_clicks)}

    @app.callback(
        # Output('output-data-upload', 'children'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        State('upload-data', 'last_modified')
    )
    def update_output(contents, filename, last_modified):

        print("Received file...")

        if contents is not None:
            content_type, content_string = contents.split(',')

            print(f"File Length: {len(content_string)}")

            decoded = base64.b64decode(content_string)

            try:
                if 'csv' in filename:
                    pass
                    # Assume that the user uploaded a CSV file
                    # df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
                elif 'xls' in filename:
                    # Assume that the user uploaded an excel file
                    # df = pd.read_excel(io.BytesIO(decoded))
                    pass
                else:
                    pass
                    # return html.Div(['There was an error processing this file.'])
            except Exception as e:
                print(e)
                # return html.Div(['There was an error processing this file.'])

            # return html.Div([
            #     html.H5(filename),
            #     html.H6(datetime.datetime.fromtimestamp(last_modified)),
            #
            #     dash_table.DataTable(
            #         data=df.to_dict('records'),
            #         columns=[{'name': i, 'id': i} for i in df.columns]
            #     )
            # ])

        # return html.Div(['No file selected'])

    @app.callback(
        Output("download-data-file", "data"),
        Input("btn-save", "n_clicks"),
        prevent_initial_call=True,
    )
    def generate_csv(n_clicks):
        # Generate some example data
        df = pd.DataFrame({
            "Column 1": ["A", "B", "C", "D"],
            "Column 2": [1, 2, 3, 4],
            "Column 3": [10.1, 20.2, 30.3, 40.4]
        })

        return dcc.send_data_frame(df.to_csv, "graph_data.csv")

    @app.callback(
        [Output('file-name', 'children'),
         Output('stored-file', 'data')],
        [Input('upload-document', 'contents')],
        [State('upload-document', 'filename'),
         State('upload-document', 'last_modified')]
    )
    def store_file(contents, filename, last_modified):
        if contents is not None:
            return html.Div([f'Selected file: {filename}']), {'contents': contents, 'filename': filename, 'last_modified': last_modified}
        return html.Div(['No file selected']), {'contents': None, 'filename': None, 'last_modified': None}

    @app.callback(
        Output('output-document-upload', 'children'),
        Input('upload-button', 'n_clicks'),
        State("socketio", "socketId"),
        State('stored-file', 'data')
    )
    def upload_document(n_clicks, socket_id, data):
        if n_clicks > 0 and data['contents'] is not None:
            contents = data['contents']
            filename = data['filename']
            last_modified = data['last_modified']

            content_type, content_string = contents.split(',')

            decoded = base64.b64decode(content_string)

            emit(
                "notification",
                "File Content Processed",
                namespace="/",
                to=socket_id
            )


            return html.Div([
                html.H5(filename),
                html.H6(datetime.fromtimestamp(last_modified))
            ])

        return html.Div(['No file selected'])

    @app.callback(
        [Input('cytoscape-graph', 'selectedNodeData'),
         Input('cytoscape-graph', 'selectedEdgeData')]
    )
    def set_selected_data(nodes, edges):

        ctx = dash.callback_context

        if not ctx.triggered:
            print('No elements selected')

        if not nodes and not edges:
            print('No elements selected')

        selected_elements = 'Selected nodes: ' + str(nodes) + '\n'
        selected_elements += 'Selected edges: ' + str(edges)

        print(selected_elements)

    @app.callback(
        Output('session-state', 'data'),
        Output('session-id', 'data'),
        Input('initial-load', 'n_clicks')
    )
    def initialize_session_state(n_clicks):

        logging.info(f"initializing")

        if n_clicks is None:
            raise PreventUpdate

        session_id = str(uuid.uuid4())
        session_data = {'initialized': True, 'value': 42}
        return session_data, session_id

    @app.callback(
        Output('output', 'children'),
        Input('session-state', 'modified_timestamp'),
        State('session-state', 'data'),
        State('session-id', 'data')

    )
    def update_output(ts, session_data, session_id):

        logging.info(f"Updating output with session ID: {session_id} and data: {session_data}")

        if ts is None:
            raise PreventUpdate

        logging.info(f"update_output: {session_id} {session_data}")

        if session_data and session_id:
            return f"Session {session_id} initialized: {session_data['initialized']} with value: {session_data['value']}"
        return "Session not initialized"

    @app.callback(
        Output("toggle-label", "children"),
        Input("search-type-toggle", "value")
    )
    def update_label(is_service):
        return "Service" if is_service else "Local"

    # Callback to toggle the modal and update the table data
    @app.callback(
        Output("modal", "is_open"),
        Output("search-results-table", "data"),
        [
            Input("search-button", "n_clicks"),
            Input("search-input", "n_submit"),
            Input("close-modal", "n_clicks")
        ],
        [
            State("search-input", "value"),
            State("modal", "is_open"),
            State("search-type-toggle", "value")
        ],
    )
    def toggle_modal(n_search, n_close, n_submit, search_value, is_open, toggle_value):

        from app import app_state

        ctx = callback_context

        if not ctx.triggered:
            return is_open, []

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        kgservice = app_state["kgraphservice"]

        if (button_id == "search-button" or button_id == "search-input") and search_value:
            # Ensure search_value is a string
            if not isinstance(search_value, str):
                search_value = ""
            try:

                logging.info(f"search service: {toggle_value}, search_value: {search_value}")

                ont_manager = kgservice.get_ontology_query_manager()

                ont_results = ont_manager.search_domain_ontology(search_value)

                filtered_data = [
                    {'Id': str(result.URI), 'Label': str(result.name), 'Type': 'Node'}
                    for result in ont_results
                ]

                # logger.info(f"Filtered data: {filtered_data}")

                return True, filtered_data

                # filtered_data = df[df['Label'].str.contains(search_value, case=False, na=False)].to_dict('records')

            except Exception as e:
                logger.info(f"Error filtering data: {e}")
                return is_open, []

        if button_id == "close-modal":
            return False, []

        return is_open, []
