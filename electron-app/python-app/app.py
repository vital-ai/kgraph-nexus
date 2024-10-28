from gevent import monkey

monkey.patch_all()

import threading
import time
import os
from kgraphservice.kgraph_service import KGraphService

import logging
logging.basicConfig(level=logging.DEBUG)

from vital_ai_vitalsigns.service.graph.virtuoso_service import VirtuosoGraphService
from vital_ai_vitalsigns.service.vital_service import VitalService
from vital_ai_vitalsigns.vitalsigns import VitalSigns
from header import create_header
from search_modal import create_modal
from graph import create_graph_list
from tab_panel import create_tabs
from data_table import create_data_table

import dash
from dash import html
from dash import dcc
from dash_resizable_panels import PanelGroup, Panel, PanelResizeHandle
import pandas as pd
from callbacks import register_callbacks
from routes import register_routes
from dash_socketio import DashSocketIO
from flask_socketio import SocketIO, emit
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from utils.config_utils import ConfigUtils

start_time = time.time()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def resource_path(relative_path):
    # base_path = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


bootstrap_icons_path = resource_path('assets/bootstrap-icons.min.css')
bootstrap_css_path = resource_path('assets/bootstrap.min.css')

# this is for the context menu
cytoscape_css_path = resource_path('assets/cytoscape-context-menus.css')

logger.info("App Before Imports in %s seconds", time.time() - start_time)

logger.info("App Imports in %s seconds", time.time() - start_time)

# this didn't work
# import warnings

# warnings.filterwarnings("ignore", category=UserWarning, message="This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.")

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app_state = {}


# Sample Data for DataTable
data = {
    "Id": ["node1", "node2", "edge1"],
    "Label": ["Node 1", "Node 2", "Edge from Node 1 to Node 2"],
    "Type": ["Node", "Node", "Edge"]
}

df = pd.DataFrame(data)

logger.info("App Dataframe in %s seconds", time.time() - start_time)

# Initialize the Dash app
app = dash.Dash(__name__, external_stylesheets=[
        # dbc.themes.BOOTSTRAP,
        # "https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.4.1/font/bootstrap-icons.min.css"
        bootstrap_css_path,
        bootstrap_icons_path,
        cytoscape_css_path
    ],
    suppress_callback_exceptions=True,
    title="Knowledge Graph Nexus")

app.server.secret_key = "Test!"

socketio = SocketIO(app.server, async_mode="gevent", logger=True, engineio_logger=True, cors_allowed_origins="*")

app.layout = html.Div(
    children=[
        dcc.Store(id='session-state', storage_type='session'),
        dcc.Store(id='session-id', storage_type='session'),
        dcc.Store(id='selected-rows-store', data=[]),
        dcc.Store(id='expand-node-store', data=None),

        html.Div(
            className="container",
            children=[
                html.Button(id='initial-load', style={'display': 'none'}),
                PanelGroup(
                    id="panel-group",
                    children=[
                        Panel(
                            id="panel-1",
                            style={'position': 'relative', 'zIndex': '1'},
                            children=[
                                create_header(),
                                create_modal(df)
                            ],
                            defaultSizePercentage=10,
                            minSizePercentage=10,
                            collapsible=False
                        ),
                        PanelResizeHandle(html.Div(id="top-resize-bar", className="resize-handle-vertical")),
                        Panel(
                            id="panel-2",
                            style={'position': 'relative', 'zIndex': '1'},
                            children=[
                                PanelGroup(
                                    id="panel-group-2",
                                    style={'position': 'relative', 'zIndex': '1'},
                                    children=[
                                        Panel(
                                            id="panel-graph",
                                            children=create_graph_list(),
                                            style={'position': 'relative', 'zIndex': '1', 'width': '100%', 'height': '100%', 'border': '1px solid black'},
                                            defaultSizePercentage=50,
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
                                                create_tabs()
                                            ],
                                            style={'position': 'relative', 'zIndex': '1', 'width': '100%', 'height': '100%', 'border': '1px solid black'},
                                            defaultSizePercentage=50,
                                            minSizePercentage=10,
                                            collapsible=False,
                                            collapsedSizePercentage=0
                                        )
                                    ],
                                    direction="horizontal"
                                )
                            ],
                            minSizePercentage=50,
                        ),
                        PanelResizeHandle(html.Div(className="resize-handle-vertical")),
                        Panel(
                            id='panel-data-table',
                            children=[
                                create_data_table(df)
                            ],
                            style={'position': 'relative', 'zIndex': '1', 'width': '100%', 'height': '100%', 'border': '1px solid black'},
                            defaultSizePercentage=30,
                            minSizePercentage=20,
                            collapsible=False,
                            collapsedSizePercentage=0
                        )
                    ],
                    direction="vertical"
                ),
                dcc.Input(id="expand-node-input", type='text', style={'display': 'none'}),
                html.Div(id="output"),
                DashSocketIO(id='socketio', eventNames=["notification"])
            ]
        ),
    ]
)


@socketio.on("connect")
def on_connect():
    print("Client connected")


@socketio.on("disconnect")
def on_disconnect():
    print("Client disconnected")


def notify(socket_id, message):
    emit(
        "notification",
        message,
        namespace="/",
        to=socket_id
    )


def background_task(stop_event):
    while not stop_event.is_set():
        time.sleep(5)
        # pass


stop_event = threading.Event()

thread = threading.Thread(target=background_task, args=(stop_event,))
thread.start()

config = ConfigUtils.load_config()

virtuoso_username = config['graph_database']['virtuoso_username']
virtuoso_password = config['graph_database']['virtuoso_password']
virtuoso_endpoint = config['graph_database']['virtuoso_endpoint']

vs = VitalSigns()

# vital_service = None

vital_graph_service = VirtuosoGraphService(
    username=virtuoso_username,
    password=virtuoso_password,
    endpoint=virtuoso_endpoint
)

vital_vector_service = None

vital_service = VitalService(
    graph_service=vital_graph_service,
    vector_service=vital_vector_service
)


kgservice = KGraphService(vital_service)

app_state["kgraphservice"] = kgservice

register_callbacks(app)

register_routes(app)

app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
    </head>
    <body>
        {%app_entry%}
        <script src="/src/cytoscape-context-menus.js" type="module"></script>
        <script src="/src/index.js" type="module"></script>
        
        <script>
        
              document.addEventListener('DOMContentLoaded', function () {

                setTimeout(function() {
                
                    
                
              
            var cytoElement = document.getElementById('cytoscape-graph');
                
            var cy = cytoElement._cyreg.cy;

        var selectAllOfTheSameType = function (type) {
          if (type == 'node') {
            cy.nodes().select();
          } else if (type == 'edge') {
            cy.edges().select();
          }
        };
        
        var unselectAllOfTheSameType = function (type) {
          if (type == 'node') {
            cy.nodes().unselect();
            ;
          } else if (type == 'edge') {
            cy.edges().unselect();
          }
        };

        var contextMenu = cy.contextMenus({
          menuItems: [
            
            {
              id: 'expand',
              content: 'expand',
              tooltipText: 'expand',
              selector: 'node',
              onClickFunction: function (event) {
                
                var target = event.target || event.cyTarget;
                var nodeId = target.id();


                console.log('target', target);
                console.log('nodeId', nodeId);
                

                let expandNodeInput = document.getElementById('expand-node-input');
                
                console.log('expandNodeInput', expandNodeInput);

                if (expandNodeInput) {
                    expandNodeInput.defaultValue = nodeId;
                    expandNodeInput.dispatchEvent(new Event('input', { bubbles: true }));
                }
                
              },
              hasTrailingDivider: true
            },
          
            {
              id: 'remove',
              content: 'remove',
              tooltipText: 'remove',
              image: {src: "assets/remove.svg", width: 12, height: 12, x: 6, y: 4},
              selector: 'node, edge',
              onClickFunction: function (event) {
                var target = event.target || event.cyTarget;
                removed = target.remove();

                contextMenu.showMenuItem('undo-last-remove');
              },
              hasTrailingDivider: true
            },
            {
              id: 'undo-last-remove',
              content: 'undo last remove',
              selector: 'node, edge',
              show: false,
              coreAsWell: true,
              onClickFunction: function (event) {
                if (removed) {
                  removed.restore();
                }
                contextMenu.hideMenuItem('undo-last-remove');
              },
              hasTrailingDivider: true
            },
            {
              id: 'color',
              content: 'change color',
              tooltipText: 'change color',
              selector: 'node',
              hasTrailingDivider: true,
              submenu: [
                {
                  id: 'color-blue',
                  content: 'blue',
                  tooltipText: 'blue',
                  onClickFunction: function (event) {
                    let target = event.target || event.cyTarget;
                    target.style('background-color', 'blue');
                  },
                  submenu: [
                    {
                      id: 'color-light-blue',
                      content: 'light blue',
                      tooltipText: 'light blue',
                      onClickFunction: function (event) {
                        let target = event.target || event.cyTarget;
                        target.style('background-color', 'lightblue');
                      },
                    },
                    {
                      id: 'color-dark-blue',
                      content: 'dark blue',
                      tooltipText: 'dark blue',
                      onClickFunction: function (event) {
                        let target = event.target || event.cyTarget;
                        target.style('background-color', 'darkblue');
                      },
                    },
                  ],
                },
                {
                  id: 'color-green',
                  content: 'green',
                  tooltipText: 'green',
                  onClickFunction: function (event) {
                    let target = event.target || event.cyTarget;
                    target.style('background-color', 'green');
                  },
                },
                {
                  id: 'color-red',
                  content: 'red',
                  tooltipText: 'red',
                  onClickFunction: function (event) {
                    let target = event.target || event.cyTarget;
                    target.style('background-color', 'red');
                  },
                },
              ]
            },
            {
              id: 'add-node',
              content: 'add node',
              tooltipText: 'add node',
              image: {src: "assets/add.svg", width: 12, height: 12, x: 6, y: 4},
              coreAsWell: true,
              onClickFunction: function (event) {
                var data = {
                  group: 'nodes'
                };

                var pos = event.position || event.cyPosition;

                cy.add({
                  data: data,
                  position: {
                    x: pos.x,
                    y: pos.y
                  }
                });
              }
            },
            {
              id: 'select-all-nodes',
              content: 'select all nodes',
              selector: 'node',
              coreAsWell: true,
              show: true,
              onClickFunction: function (event) {
                selectAllOfTheSameType('node');

                // contextMenu.hideMenuItem('select-all-nodes');
                // contextMenu.showMenuItem('unselect-all-nodes');
              }
            },
            {
              id: 'unselect-all-nodes',
              content: 'unselect all nodes',
              selector: 'node',
              coreAsWell: true,
              show: false,
              onClickFunction: function (event) {
                unselectAllOfTheSameType('node');

                // contextMenu.showMenuItem('select-all-nodes');
                // contextMenu.hideMenuItem('unselect-all-nodes');
              }
            },
            {
              id: 'select-all-edges',
              content: 'select all edges',
              selector: 'edge',
              coreAsWell: true,
              show: true,
              onClickFunction: function (event) {
                selectAllOfTheSameType('edge');

                // contextMenu.hideMenuItem('select-all-edges');
                // contextMenu.showMenuItem('unselect-all-edges');
              }
            },
            {
              id: 'unselect-all-edges',
              content: 'unselect all edges',
              selector: 'edge',
              coreAsWell: true,
              show: false,
              onClickFunction: function (event) {
                unselectAllOfTheSameType('edge');

                // contextMenu.showMenuItem('select-all-edges');
                // contextMenu.hideMenuItem('unselect-all-edges');
              }
            }
          ]
        });
        
        
          }, 1000);

        
        
      });
        
       
        </script>
        
        
        
        <footer>
            {%config%}
            {%scripts%}
            <script>
            
                var sessionId;

                document.addEventListener('DOMContentLoaded', function() {
                    console.log("DOMContentLoaded event triggered");

                    var observer = new MutationObserver(function(mutations, me) {
                        var initialLoadButton = document.getElementById('initial-load');
                        if (initialLoadButton) {
                            console.log("Initial load button found, clicking it");
                            initialLoadButton.click();
                            me.disconnect();
                            setTimeout(checkSessionIdStore, 500); // Check for session-id store after initial load
                            return;
                        }
                    });

                    // Start observing for initial load button
                    observer.observe(document, {
                        childList: true,
                        subtree: true
                    });

                    function checkSessionIdStore() {
                        var s = JSON.parse(sessionStorage.getItem('session-id'))
                        // check to see if this is really set
                        
                        sessionId = s;
                    }

                    function sendSessionId() {
                        if (sessionId) {
                            console.log("Sending session ID:", sessionId);
                            var payload = JSON.stringify({session_id: sessionId});
                            navigator.sendBeacon("/release_state", payload);
                        } else {
                            console.log("Session ID not set, cannot send");
                        }
                    }

                    window.addEventListener('beforeunload', sendSessionId);
                    window.addEventListener('unload', sendSessionId);
                    
                });
            </script>
            {%renderer%}
        </footer>
    </body>
</html>
'''


if __name__ == '__main__':
    logger.info("Starting app")
    logger.info("App runtime started in %s seconds", time.time() - start_time)

    port = 9000

    try:
        server = app.server
        http_server = WSGIServer(('0.0.0.0', 9000), server, handler_class=WebSocketHandler)
        http_server.serve_forever()
        # app.run_server(port=port, debug=False, dev_tools_ui=False)
    except KeyboardInterrupt:
        stop_event.set()
        thread.join()
        print("Server stopped gracefully")
