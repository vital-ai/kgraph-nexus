from vital_ai_vitalsigns.metaql.query.property_data_constraint_utils import PropertyDataConstraintUtils
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from utils.config_utils import ConfigUtils
from kgnexus.kgnexus_manager import KGNexusManager


def main():

    print('Test KGraphService Manager ')

    vs = VitalSigns()

    print("VitalSigns Initialized")

    config = ConfigUtils.load_config()

    wordnet_graph_uri = 'http://vital.ai/graph/wordnet-frames-graph-1'

    manager = KGNexusManager(
        kgraphservice_name="local_kgraphservice"
    )

    manager.search(
        graph_uri=wordnet_graph_uri,
        search_string="happy",
        offset=0, limit=100
    )

    happy_uri = "http://vital.ai/haley.ai/app/KGEntity/1716488384292_691801398"

    manager.expand(
        graph_uri=wordnet_graph_uri,
        node_uri=happy_uri,
        offset=0, limit=100
    )


if __name__ == "__main__":
    main()
