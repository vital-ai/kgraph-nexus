import json
from ai_haley_kg_domain.model.KGEntity import KGEntity
from ai_haley_kg_domain.model.KGFrame import KGFrame
from ai_haley_kg_domain.model.KGSlot import KGSlot
from ai_haley_kg_domain.model.properties.Property_hasEntitySlotValue import Property_hasEntitySlotValue
from ai_haley_kg_domain.model.properties.Property_hasKGSlotType import Property_hasKGSlotType
from ai_haley_kg_domain.model.properties.Property_hasKGraphDescription import Property_hasKGraphDescription
from vital_ai_vitalsigns.metaql.arc.metaql_arc import ARC_TRAVERSE_TYPE_PROPERTY
from vital_ai_vitalsigns.metaql.query.query_builder import QueryBuilder, AndConstraintList, PropertyConstraint, \
    ConstraintType, ClassConstraint, Arc, OrConstraintList, NodeBind, EdgeBind, PathBind, PropertyPathList, \
    MetaQLPropertyPath, AndArcList, OrArcList, SolutionBind
from vital_ai_vitalsigns.model.GraphObject import GraphObject
from vital_ai_vitalsigns.model.VITAL_Edge import VITAL_Edge
from vital_ai_vitalsigns.utils.uri_generator import URIGenerator
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from vital_ai_vitalsigns_core.model.properties.Property_URIProp import Property_URIProp
from vital_ai_vitalsigns_core.model.properties.Property_hasName import Property_hasName
from kgraphservice.kgraph_service_rest import KGraphServiceREST


class KGNexusManager:
    def __init__(self, *, kgraphservice_name: str):
        self._kgraphservice_name = kgraphservice_name
        self._rest_client = KGraphServiceREST()

    def search(self, *, graph_uri: str, search_string: str, offset: int, limit: int) -> list:

        search_result_list = []

        sq = (
            QueryBuilder.select_query(
                offset=offset,
                limit=limit
            )
            .graph_uri(graph_uri)
            .constraint_list(
                AndConstraintList()
                .node_constraint(
                    PropertyConstraint(
                        property=Property_hasKGraphDescription.get_uri(),
                        comparator=ConstraintType.STRING_CONTAINS,
                        value=search_string
                    )
                )
                .node_constraint(
                    ClassConstraint(
                        clazz=KGEntity.get_class_uri()
                    )
                )
            )
            .build()
        )

        print(sq)

        metaql_sq_query_results = self._rest_client.metaql_select_query(select_query=sq)

        print(metaql_sq_query_results)

        result_list = metaql_sq_query_results.get_result_list()

        count = 0

        for re in result_list:
            graph_object = re.graph_object
            score = re.score
            uri = graph_object.URI
            name = graph_object.name
            count += 1

            print(f"({count}) GraphObject (score={score}): Name: {str(name)}, URI: {str(uri)} | {graph_object}")
            search_result_list.append(graph_object)

        return search_result_list

    def expand(self, *, graph_uri: str, node_uri: str, offset: int, limit: int) -> list:

        gq = (
            QueryBuilder.graph_query(
                offset=offset,
                limit=limit,
                resolve_objects=True
            )
            .graph_uri(graph_uri)
            .arc(
                Arc()
                .node_bind(NodeBind(name="frame"))
                .constraint_list(
                    AndConstraintList()
                    .node_constraint(
                        ClassConstraint(
                            clazz=KGFrame.get_class_uri()
                        )
                    )
                )
                .arc_list(
                    OrArcList()
                    .arc_list(
                        AndArcList()
                        .arc(
                            Arc()
                            .node_bind(NodeBind(name="source_slot"))
                            .edge_bind(EdgeBind(name="source_slot_edge"))
                            .constraint_list(
                                AndConstraintList()
                                .node_constraint(
                                    PropertyConstraint(
                                        property=Property_hasKGSlotType.get_uri(),
                                        comparator=ConstraintType.EQUAL_TO,
                                        value="urn:hasSourceEntity"
                                    )
                                )
                                .node_constraint(
                                    ClassConstraint(
                                        clazz=KGSlot.get_class_uri(),
                                        include_subclasses=True
                                    )
                                )
                            )
                            .arc(
                                Arc(arc_traverse_type=ARC_TRAVERSE_TYPE_PROPERTY)
                                .solution_bind(SolutionBind(name="entity"))
                                .node_bind(NodeBind(name="source_entity"))  # source_entity
                                .path_bind(PathBind(name="source_entity_path"))
                                .property_path_list(
                                    PropertyPathList()
                                    .property_path(
                                        MetaQLPropertyPath(
                                            property_uri=Property_hasEntitySlotValue.get_uri()
                                        )
                                    )
                                )
                                .constraint_list(
                                    AndConstraintList()
                                    .node_constraint(
                                        PropertyConstraint(
                                            property=Property_URIProp.get_uri(),
                                            comparator=ConstraintType.EQUAL_TO,
                                            value=node_uri
                                        )
                                    )
                                    .node_constraint(
                                        ClassConstraint(
                                            clazz=KGEntity.get_class_uri()
                                        )
                                    )
                                )
                            )
                        )
                        .arc(
                            Arc()
                            .node_bind(NodeBind(name="destination_slot"))
                            .edge_bind(EdgeBind(name="destination_slot_edge"))
                            .constraint_list(
                                AndConstraintList()
                                .node_constraint(
                                    PropertyConstraint(
                                        property=Property_hasKGSlotType.get_uri(),
                                        comparator=ConstraintType.EQUAL_TO,
                                        value="urn:hasDestinationEntity"
                                    )
                                )
                                .node_constraint(
                                    ClassConstraint(
                                        clazz=KGSlot.get_class_uri(),
                                        include_subclasses=True
                                    )
                                )
                            )
                            .arc(
                                Arc(arc_traverse_type=ARC_TRAVERSE_TYPE_PROPERTY)
                                .node_bind(NodeBind(name="destination_entity"))
                                .path_bind(PathBind(name="destination_entity_path"))
                                .property_path_list(
                                    PropertyPathList()
                                    .property_path(
                                        MetaQLPropertyPath(
                                            property_uri=Property_hasEntitySlotValue.get_uri()
                                        )
                                    )
                                )
                                .constraint_list(
                                    AndConstraintList()
                                    .node_constraint(
                                        ClassConstraint(
                                            clazz=KGEntity.get_class_uri()
                                        )
                                    )
                                )
                            )
                        )
                    )
                    .arc_list(
                        AndArcList()
                        .arc(
                            Arc()
                            .node_bind(NodeBind(name="source_slot"))
                            .edge_bind(EdgeBind(name="source_slot_edge"))
                            .constraint_list(
                                AndConstraintList()
                                .node_constraint(
                                    PropertyConstraint(
                                        property=Property_hasKGSlotType.get_uri(),
                                        comparator=ConstraintType.EQUAL_TO,
                                        value="urn:hasSourceEntity"
                                    )
                                )
                                .node_constraint(
                                    ClassConstraint(
                                        clazz=KGSlot.get_class_uri(),
                                        include_subclasses=True
                                    )
                                )
                            )
                            .arc(
                                Arc(arc_traverse_type=ARC_TRAVERSE_TYPE_PROPERTY)
                                .node_bind(NodeBind(name="source_entity"))
                                .path_bind(PathBind(name="source_entity_path"))
                                .property_path_list(
                                    PropertyPathList()
                                    .property_path(
                                        MetaQLPropertyPath(
                                            property_uri=Property_hasEntitySlotValue.get_uri()
                                        )
                                    )
                                )
                                .constraint_list(
                                    AndConstraintList()
                                    .node_constraint(
                                        ClassConstraint(
                                            clazz=KGEntity.get_class_uri()
                                        )
                                    )
                                )
                            )
                        )
                        .arc(
                            Arc()
                            .node_bind(NodeBind(name="destination_slot"))
                            .edge_bind(EdgeBind(name="destination_slot_edge"))
                            .constraint_list(
                                AndConstraintList()
                                .node_constraint(
                                    PropertyConstraint(
                                        property=Property_hasKGSlotType.get_uri(),
                                        comparator=ConstraintType.EQUAL_TO,
                                        value="urn:hasDestinationEntity"
                                    )
                                )
                                .node_constraint(
                                    ClassConstraint(
                                        clazz=KGSlot.get_class_uri(),
                                        include_subclasses=True
                                    )
                                )
                            )
                            .arc(
                                Arc(arc_traverse_type=ARC_TRAVERSE_TYPE_PROPERTY)
                                .solution_bind(SolutionBind(name="entity"))
                                .node_bind(NodeBind(name="destination_entity"))  # destination_entity
                                .path_bind(PathBind(name="destination_entity_path"))
                                .property_path_list(
                                    PropertyPathList()
                                    .property_path(
                                        MetaQLPropertyPath(
                                            property_uri=Property_hasEntitySlotValue.get_uri()
                                        )
                                    )
                                )
                                .constraint_list(
                                    AndConstraintList()
                                    .node_constraint(
                                        PropertyConstraint(
                                            property=Property_URIProp.get_uri(),
                                            comparator=ConstraintType.EQUAL_TO,
                                            value=node_uri
                                        )
                                    )
                                    .node_constraint(
                                        ClassConstraint(
                                            clazz=KGEntity.get_class_uri()
                                        )
                                    )
                                )
                            )
                        )
                    )
                )
            )
            .build()
        )

        print(gq)

        graph_query_json = json.dumps(gq, indent=4)

        print(f"Query JSON:\n{graph_query_json}")

        expand_results = []

        metaql_result = self._rest_client.metaql_graph_query(graph_query=gq)

        print(metaql_result)

        binding_list = metaql_result.get_binding_list()

        print(f"Binding List: {binding_list}")

        result_object_list = metaql_result.get_result_object_list()

        object_map = {}

        for go in result_object_list:
            print(f"Result Object: {go.to_json()}")
            uri = str(go.URI)
            object_map[uri] = go

        rl = metaql_result.get_result_list()

        # potentially group into "frame parts"
        # which would leave:

        # frame (node)
        # --edge--> entity1 (node)
        # --edge--> entity2 (node)
        # this could handle N entities participating in the frame

        # for 2 entity frames like wordnet this could be grouped into:
        # entity --frame-edge--> entity

        # wordnet is directional so the frame-edge had a definite direction

        # in other cases, like a symmetric frame, a direction could be arbitrary
        # or both directional edges asserted like:
        # a --friend-frame--> b
        # b --friend-frame--> a

        for re in rl:
            print(f"ResultElement: {re}")
            go: GraphObject = re.graph_object
            print(f"ResultElement GraphMatch GO: {go.to_json(pretty_print=False)}")

            # slot --> entity cases
            # add in as "virtual" edges

            source_entity_uri = str(go["source_entity"])
            destination_entity_uri = str(go["destination_entity"])
            source_entity_path_uri = str(go["source_entity_path"])
            destination_entity_path_uri = str(go["destination_entity_path"])

            edge_source = VITAL_Edge()
            edge_source.URI = URIGenerator.generate_uri()
            edge_source.edgeSource = source_entity_path_uri
            edge_source.edgeDestination = source_entity_uri

            edge_destination = VITAL_Edge()
            edge_destination.URI = URIGenerator.generate_uri()
            edge_destination.edgeSource = destination_entity_path_uri
            edge_destination.edgeDestination = destination_entity_uri

            expand_results.extend([edge_source, edge_destination])

            for b in binding_list:
                b_uri = str(go[b])
                bind_object: GraphObject = object_map.get(b_uri, None)
                if bind_object:
                    print(f"Binding: {b} => {bind_object.to_json(pretty_print=False)}")
                else:
                    print(f"Binding: {b} => URI: {b_uri}")

        for v in object_map.values():
            expand_results.append(v)

        return expand_results




