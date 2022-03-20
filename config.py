# Open vSwitch port status monitoring interval in seconds
Interval = 1
# MongoDB URI
MongoURI = "mongodb://127.0.0.1:27017/"

ConnectedSwitchPort = {
    "02:92:b4:89:d6:8f": "02:8f:66:ba:35:6c"
}

Switch = [
    {
        "name": "sw1",
        "dpid": "0000aae305428d4a",
        "ports": [
            {
                "ip": "10.10.10.1",
                "hwaddr": "02:63:be:2b:6f:30"
            },
            {
                "ip": "10.10.10.2",
                "hwaddr": "02:c6:84:16:8a:f3"
            },
            {
                "ip": "10.10.10.3",
                "hwaddr": "02:8f:66:ba:35:6c"
            },
            {
                "ip": "10.10.10.6",
                "hwaddr": "02:2a:41:1e:70:d0"
            }
        ]
    },
    {
        "name": "sw2",
        "dpid": "0000c699ecb9ea46",
        "ports": [
            {
                "ip": "10.10.10.7",
                "hwaddr": "02:64:b5:00:eb:96"
            },
            {
                "ip": "10.10.10.4",
                "hwaddr": "02:3b:1b:85:e8:f2"
            },
            {
                "ip": "10.10.10.5",
                "hwaddr": "02:d2:2a:d1:64:e6"
            },
            {
                "ip": "10.10.10.13",
                "hwaddr": "02:92:b4:89:d6:8f"
            }
        ]
    }
]

NodeList = [
    {
        "ip": "10.10.10.11",
        "name": "server",
        "hwaddr": "02:08:b5:7d:6f:85",
        "port": "02:63:be:2b:6f:30",
        "cache": True,
    },
    {
        "ip": "10.10.10.12",
        "name": "sw1c1",
        "hwaddr": "02:38:d0:c7:9c:d9",
        "port": "02:c6:84:16:8a:f3"
    },
    {
        "ip": "10.10.10.16",
        "name": "sw1c2",
        "hwaddr": "02:fb:0d:7f:2d:5c",
        "port": "02:2a:41:1e:70:d0"
    },
    {
        "ip": "10.10.10.14",
        "name": "sw2c1",
        "hwaddr": "02:df:10:16:cb:2f",
        "port": "02:3b:1b:85:e8:f2"
    },
    {
        "ip": "10.10.10.15",
        "name": "sw2c2",
        "hwaddr": "02:9c:63:fb:08:b7",
        "port": "02:d2:2a:d1:64:e6"
    },
    {
        "ip": "10.10.10.17",
        "name": "cache1",
        "hwaddr": "02:de:9b:97:19:1c",
        "port": "02:64:b5:00:eb:96",
        "cache": True,
    },
]


def get_cache_list():
    cache_server = []
    for node in NodeList:
        if "cache" in node.keys() and node["cache"] is True:
            cache_server.append(node)
    return cache_server


def port_to_node(port_addr):
    for node in NodeList:
        if node["port"] == port_addr:
            return node["ip"], node["name"]


def dpid_to_name(dpid):
    for sw in Switch:
        if sw["dpid"] == dpid:
            return sw["name"]


def port_addr_to_node_name(port_addr):
    for node in NodeList:
        if node["port"] == port_addr:
            return node["name"]
    sw_port = ""
    for k in ConnectedSwitchPort.keys():
        if k == port_addr:
            sw_port = ConnectedSwitchPort[k]
            break
        elif ConnectedSwitchPort[k] == port_addr:
            sw_port = k
            break
    for sw in Switch:
        for port in sw["ports"]:
            if port["hwaddr"] == sw_port:
                return sw["name"]
