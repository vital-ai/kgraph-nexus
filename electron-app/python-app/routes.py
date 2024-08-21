import json
import logging
import os

import flask
from dash import Input, Output, State
from flask import request, jsonify, send_from_directory
import pandas as pd
from kgraphservice.query.construct_query import ConstructQuery
from rdflib import Graph, URIRef, Literal
from vital_ai_vitalsigns.ontology.ontology import Ontology
from vital_ai_vitalsigns.service.graph.binding import Binding, BindingValueType
from vital_ai_vitalsigns_core.model.RDFStatement import RDFStatement


# mainly use callbacks but can access routes as needed
# routes used for testing and with tulip plugin


def register_routes(app):

    @app.server.route('/src/<path:path>')
    def serve_src(path):
        print(f"Serving file from /src: {path}")
        return send_from_directory(os.path.join(os.getcwd(), 'src'), path)

    @app.server.route('/release_state', methods=['POST'])
    def release_state():
        logging.info(f'Releasing state request: {request}')
        raw_data = request.get_data(as_text=True)
        data = json.loads(raw_data)
        # data = request.json
        session_id = data.get('session_id')
        if session_id:
            # Release state logic here for the given session_id
            logging.info(f'Releasing state for session: {session_id}')
        return jsonify(success=True)

    @app.server.route('/health', methods=['GET'])
    def health_check():
        logging.info('Health Check')
        return jsonify({'status': 'ok'})

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

        from app import app_state

        kgservice = app_state["kgraphservice"]

        wordnet_frame_graph_uri = "http://vital.ai/graph/wordnet-frames-graph-1"

        # search_string = "happy"

        search_string = data.get("search_string")

        vital_graph_service = kgservice.vital_service.graph_service

        namespace_list = get_default_namespace_list()

        binding_list = [
            Binding("?uri", "urn:hasUri"),
            ]

        select_query = f"""
                   ?uri a haley-ai-kg:KGEntity ;
                        haley-ai-kg:hasKGraphDescription ?description .
                        ?description bif:contains "{search_string}" .                   
                   """

        construct_query = ConstructQuery(namespace_list, binding_list, select_query)

        result_list = vital_graph_service.query_construct(
            wordnet_frame_graph_uri,
            construct_query.query,
            construct_query.namespace_list,
            construct_query.binding_list,
            limit=500, offset=0
        )

        graph = Graph()

        for result in result_list:
            rs = result.graph_object
            if isinstance(rs, RDFStatement):
                s = rs.rdfSubject
                p = rs.rdfPredicate

                value_type = BindingValueType.URIREF

                for binding in construct_query.binding_list:
                    if binding.property_uri == str(p):
                        value_type = binding.value_type
                        break

                o = rs.rdfObject
                if value_type == BindingValueType.URIREF:
                    graph.add((URIRef(str(s)), URIRef(str(p)), URIRef(str(o))))
                else:
                    graph.add((URIRef(str(s)), URIRef(str(p)), Literal(str(o))))

        subjects = set(graph.subjects())

        num_unique_subjects = len(subjects)

        print(f"Wordnet Solution Count: {num_unique_subjects}")

        subject_set = set()

        for triple in graph.triples((None, None, None)):
            [s, p, o] = triple

            if p == URIRef("urn:hasUri"):
                subject_set.add((str(o)))

        print(f"Getting objects count: {len(subject_set)}")

        result_list = vital_graph_service.get_object_list_bulk(
            list(subject_set),
            graph_uri=wordnet_frame_graph_uri)

        graph_object_list = []

        for obj in result_list:
            go = obj.graph_object
            graph_object_list.append(go)

        go_map_list = []

        for g in graph_object_list:
            g_json_string = g.to_json()
            g_map = json.loads(g_json_string)
            go_map_list.append(g_map)

        print(f"Got objects count: {len(graph_object_list)}")

        return jsonify({'status': 'ok', 'result_list': go_map_list})

    @app.server.route('/graph-query', methods=['POST'])
    def handle_graph_query():
        data = request.get_json()
        logging.info(f"Received at /graph-query: {data}")

        from app import app_state

        kgservice = app_state["kgraphservice"]

        wordnet_frame_graph_uri = "http://vital.ai/graph/wordnet-frames-graph-1"

        node_list = data.get("node_list")

        node_list_string = "\n".join(f"<{uri}>" for uri in node_list)

        vital_graph_service = kgservice.vital_service.graph_service

        namespace_list = get_default_namespace_list()

        binding_list = [
            Binding("?uri", "urn:hasUri"),
            Binding("?frame", "urn:hasFrame"),
            Binding("?sourceSlot", "urn:hasSourceSlot"),
            Binding("?destinationSlot", "urn:hasDestinationSlot"),
            Binding("?sourceSlotEntity", "urn:hasSourceSlotEntity"),
            Binding("?destinationSlotEntity", "urn:hasDestinationSlotEntity"),
            Binding("?destinationEdge", "urn:hasDestinationEdge"),
            Binding("?sourceEdge", "urn:hasSourceEdge")
        ]

        frame_query = f"""
                  VALUES ?uri {{ 
                    { node_list_string }
                    }}
                    
                  ?uri a haley-ai-kg:KGEntity .
                       
                  {{
                    ?sourceEdge a haley-ai-kg:Edge_hasKGSlot ;
                                vital-core:hasEdgeSource ?frame ;
                                vital-core:hasEdgeDestination ?sourceSlot .
                    ?sourceSlot a haley-ai-kg:KGEntitySlot ;
                                haley-ai-kg:hasEntitySlotValue ?uri ;
                                haley-ai-kg:hasKGSlotType <urn:hasSourceEntity> .
                    ?destinationEdge a haley-ai-kg:Edge_hasKGSlot ;
                                     vital-core:hasEdgeSource ?frame ;
                                     vital-core:hasEdgeDestination ?destinationSlot .
                    ?destinationSlot a haley-ai-kg:KGEntitySlot ;
                                     haley-ai-kg:hasEntitySlotValue ?destinationSlotEntity ;
                                     haley-ai-kg:hasKGSlotType <urn:hasDestinationEntity> .
                    BIND(?uri AS ?sourceSlotEntity)
                  }}
                  UNION
                  {{
                    ?destinationEdge a haley-ai-kg:Edge_hasKGSlot ;
                                     vital-core:hasEdgeSource ?frame ;
                                     vital-core:hasEdgeDestination ?destinationSlot .
                    ?destinationSlot a haley-ai-kg:KGEntitySlot ;
                                     haley-ai-kg:hasEntitySlotValue ?uri ;
                                     haley-ai-kg:hasKGSlotType <urn:hasDestinationEntity> .
                    ?sourceEdge a haley-ai-kg:Edge_hasKGSlot ;
                                vital-core:hasEdgeSource ?frame ;
                                vital-core:hasEdgeDestination ?sourceSlot .
                    ?sourceSlot a haley-ai-kg:KGEntitySlot ;
                                haley-ai-kg:hasEntitySlotValue ?sourceSlotEntity ;
                                haley-ai-kg:hasKGSlotType <urn:hasSourceEntity> .
                    BIND(?uri AS ?destinationSlotEntity)
                  }}
                  """

        construct_query = ConstructQuery(namespace_list, binding_list, frame_query)

        result_list = vital_graph_service.query_construct(
            wordnet_frame_graph_uri,
            construct_query.query,
            construct_query.namespace_list,
            construct_query.binding_list,
            limit=500, offset=0
        )

        graph = Graph()

        for result in result_list:
            rs = result.graph_object
            if isinstance(rs, RDFStatement):
                s = rs.rdfSubject
                p = rs.rdfPredicate

                value_type = BindingValueType.URIREF

                for binding in construct_query.binding_list:
                    if binding.property_uri == str(p):
                        value_type = binding.value_type
                        break

                o = rs.rdfObject
                if value_type == BindingValueType.URIREF:
                    graph.add((URIRef(str(s)), URIRef(str(p)), URIRef(str(o))))
                else:
                    graph.add((URIRef(str(s)), URIRef(str(p)), Literal(str(o))))

        subjects = set(graph.subjects())

        num_unique_subjects = len(subjects)

        print(f"Wordnet Solution Count: {num_unique_subjects}")

        subject_set = set()

        for triple in graph.triples((None, None, None)):
            [s, p, o] = triple

            if p == URIRef("urn:hasUri"):
                subject_set.add((str(o)))

            if p == URIRef("urn:hasFrame"):
                subject_set.add((str(o)))

            if p == URIRef("urn:hasSourceSlot"):
                subject_set.add((str(o)))

            if p == URIRef("urn:hasDestinationSlot"):
                subject_set.add((str(o)))

            if p == URIRef("urn:hasSourceSlotEntity"):
                subject_set.add((str(o)))

            if p == URIRef("urn:hasDestinationSlotEntity"):
                subject_set.add((str(o)))

            if p == URIRef("urn:hasSourceEdge"):
                subject_set.add((str(o)))

            if p == URIRef("urn:hasDestinationEdge"):
                subject_set.add((str(o)))



        print(f"Getting objects count: {len(subject_set)}")

        result_list = vital_graph_service.get_object_list_bulk(
            list(subject_set),
            graph_uri=wordnet_frame_graph_uri)

        graph_object_list = []

        for obj in result_list:
            go = obj.graph_object
            graph_object_list.append(go)

        go_map_list = []

        for g in graph_object_list:
            g_json_string = g.to_json()
            g_map = json.loads(g_json_string)
            go_map_list.append(g_map)

        print(f"Got objects count: {len(graph_object_list)}")

        return jsonify({'status': 'ok', 'result_list': go_map_list})

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

    def get_default_namespace_list():
        namespace_list = [
            Ontology("vital-core", "http://vital.ai/ontology/vital-core#"),
            Ontology("vital", "http://vital.ai/ontology/vital#"),
            Ontology("vital-aimp", "http://vital.ai/ontology/vital-aimp#"),
            Ontology("haley", "http://vital.ai/ontology/haley"),
            Ontology("haley-ai-question", "http://vital.ai/ontology/haley-ai-question#"),
            Ontology("haley-ai-kg", "http://vital.ai/ontology/haley-ai-kg#")
        ]

        return namespace_list
