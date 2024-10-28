import base64
import io
import json
import logging
import uuid
from datetime import datetime
import flask
import kgraphservice
import networkx as nx
from dash import dcc, html, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
from flask import request, jsonify
import pandas as pd
import dash
from flask_socketio import SocketIO, emit
from vital_ai_vitalsigns.model.VITAL_Edge import VITAL_Edge
from vital_ai_vitalsigns.model.VITAL_Node import VITAL_Node

from kgnexus.kgnexus_manager import KGNexusManager


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
        session_data = {'initialized': True}
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
            return f"Session {session_id} initialized: {session_data['initialized']}"
        return "Session not initialized"

    @app.callback(
        Output("toggle-label", "children"),
        Input("search-type-toggle", "value")
    )
    def update_label(is_service):
        return "Service" if is_service else "Local"

    @app.callback(
        Output('selected-rows-store', 'data'),
        Input('search-results-table', 'derived_virtual_selected_rows'),
        prevent_initial_call=True
    )
    def log_selected_rows(selected_rows):
        print(f"Selected rows: {selected_rows}")
        return selected_rows

    @app.callback(
        Output('cytoscape-graph', 'elements', allow_duplicate=True),
        Input('expand-node-input', 'value'),
        State('cytoscape-graph', 'elements'),
        prevent_initial_call=True
    )
    def handle_expand_node_click(node_data, current_elements):

        print(f"Expanding node data: {node_data}")

        if node_data is None:
            return dash.no_update

        try:
            # node_data = pd.read_json(node_data) if isinstance(node_data, str) else node_data
            # node_id = node_data.get("node_id")
            print(f"Expanding node ID: {node_data}")

            node_uri = node_data

            kgraphservice_manager = KGNexusManager(
                kgraphservice_name="local_kgraphservice",
            )

            wordnet_graph_uri = 'http://vital.ai/graph/wordnet-frames-graph-1'

            expand_results = kgraphservice_manager.expand(
                graph_uri=wordnet_graph_uri,
                node_uri=node_uri,
                limit=100, offset=0
            )

            graph_elements = []

            for g in expand_results:
                if isinstance(g, VITAL_Node):
                    node = {'data': {'id': str(g.URI), 'label': str(g.name)}, 'position': {'x': 75, 'y': 75}}
                    graph_elements.append(node)
                if isinstance(g, VITAL_Edge):
                    edge = {'data': {'id': str(g.URI), 'source': str(g.edgeSource), 'target': str(g.edgeDestination)}}
                    graph_elements.append(edge)

            updated_graph = current_elements + graph_elements

            graph = nx.Graph()

            for element in updated_graph:
                if 'source' not in element['data']:  # it's a node
                    node_id = element['data']['id']
                    graph.add_node(node_id)

                # Add edges
            for element in updated_graph:
                if 'source' in element['data']:  # it's an edge
                    source = element['data']['source']
                    target = element['data']['target']
                    graph.add_edge(source, target)

            positions = nx.spring_layout(graph, scale=200)

            updated_elements = []

            for element in updated_graph:
                if 'source' not in element['data']:
                    node_id = element['data']['id']
                    pos = positions[node_id]
                    element['position'] = {'x': pos[0], 'y': pos[1]}
                updated_elements.append(element)

            return updated_elements

        except Exception as e:
            logging.error(f"Error handling node click: {e}")

        return current_elements

    # @app.callback(
    #    Output('expand-node-store', 'data', allow_duplicate=True),
    #    Input('cytoscape-graph', 'elements'),
    #    prevent_initial_call=True
    #)
    #def clear_expand_node(elements):
    #    # Clear the clicked-node-store after the elements have been updated
    #    return None

    # Callback to toggle the modal and update the table data
    @app.callback(
        Output("modal", "is_open"),
        Output("search-results-table", "data"),
        Output("search-results-table", "selected_rows"),

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
            return is_open, [], []

        button_id = ctx.triggered[0]['prop_id'].split('.')[0]

        kgservice = app_state["kgraphservice"]

        if (button_id == "search-button" or button_id == "search-input") and search_value:
            # Ensure search_value is a string
            if not isinstance(search_value, str):
                search_value = ""
            try:

                logging.info(f"search service: {toggle_value}, search_value: {search_value}")

                # ont_manager = kgservice.get_ontology_query_manager()

                # ont_results = ont_manager.search_domain_ontology(search_value)

                kgraphservice_manager = KGNexusManager(
                    kgraphservice_name="local_kgraphservice",
                )

                wordnet_graph_uri = 'http://vital.ai/graph/wordnet-frames-graph-1'

                search_result_list = kgraphservice_manager.search(
                    graph_uri=wordnet_graph_uri,
                    search_string=search_value,
                    limit=100, offset=0
                )

                filtered_data = []

                for g in search_result_list:
                    node = {
                        'Id': str(g.URI),
                        'Label': str(g.name),
                        'Type': 'Node'
                    }

                    filtered_data.append(node)

                # filtered_data = [
                #    {
                #        'Id': str(result.URI),
                #        'Label': str(result.name),
                #        'Type': 'Node'
                #    }
                #    for result in ont_results
                # ]

                # logger.info(f"Filtered data: {filtered_data}")

                return True, filtered_data, []

                # filtered_data = df[df['Label'].str.contains(search_value, case=False, na=False)].to_dict('records')

            except Exception as e:
                logger.info(f"Error filtering data: {e}")
                return is_open, [], []

        if button_id == "close-modal":
            return False, [], []

        return is_open, [], []

    @app.callback(
        Output('cytoscape-graph', 'elements', allow_duplicate=True),
        Output('graph-elements-store', 'data'),
        Input('add-to-graph-button', 'n_clicks'),
        State('selected-rows-store', 'data'),
        State('search-results-table', 'data'),
        State('cytoscape-graph', 'elements'),
        prevent_initial_call=True
    )
    def add_nodes_to_graph(n_clicks, selected_rows, table_data, current_elements):

        print(f"Add Nodes for Selected rows: {selected_rows}")

        if n_clicks > 0 and selected_rows:

            selected_nodes = [table_data[row] for row in selected_rows]

            # Check if nodes already exist in the graph
            existing_node_ids = {element['data']['id'] for element in current_elements if 'data' in element}

            new_nodes = []

            for node in selected_nodes:
                if node['Id'] not in existing_node_ids:
                    new_node = {
                        'data': {'id': node['Id'], 'label': node['Label']},
                        'position': {'x': 300, 'y': 300}
                    }
                    new_nodes.append(new_node)

            updated_elements = current_elements + new_nodes

            return updated_elements, updated_elements

        return current_elements, current_elements
