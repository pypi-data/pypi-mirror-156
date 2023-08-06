

class RYU:
    """
    String constants related to RYU
    """
    CONTROLLERS_PREFIX = "csle_ryu.controllers."
    OFCTL_REST_APP = "ryu.app.ofctl_rest"
    OFCTL_REST_QOS_APP = "ryu.app.rest_qos"
    OFCTL_REST_TOPOLOGY = "ryu.app.rest_topology"
    OFCTL_WS_TOPOLOGY = "ryu.app.ws_topology"
    OFCTL_GUI_TOPOLOGY = "ryu.app.gui_topology.gui_topology"
    OBSERVE_LINKS = "--observe-links"
    APP_LISTS_ARG = "--app-lists"
    LOG_FILE_ARG = "--log-file"
    CONTROLLER_PORT_ARG = "--ofp-tcp-listen-port"
    WEB_APP_PORT_ARG = "--wsapi-port"
    RYU_MANAGER = "/root/miniconda3/bin/ryu-manager"
    PACKET_BUFFER_MAX_LEN = 512
    NORTHBOUND_API_APP_NAME = "learning_switch_controller_northbound_api_app"


class CONTROLLERS:
    """
    RYU Controllers in CSLE
    """
    LEARNING_SWITCH_CONTROLLER = "learning_switch_controller"
    LEARNING_SWITCH_STP_CONTROLLER = "learning_switch_stp_controller"