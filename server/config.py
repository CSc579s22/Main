import sys

# Open vSwitch port status monitoring interval in seconds
Interval = 1
# MongoDB URI
MongoURI = "mongodb://mongo:27017/"
MaxInt = sys.maxsize

# Enable SABR cache server selection based on bandwidth estimation from SABR paper
EnableSABR = True

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

NodeList = [{'hwaddr': '02:91:1d:8c:0b:9d',
             'ip': '10.1.1.1',
             'name': 'server',
             'port': '02:83:72:02:3f:0b'},
            {'hwaddr': '02:3f:ba:31:2f:76',
             'ip': '10.10.1.1',
             'name': 'sw1c1',
             'port': '02:60:81:9a:80:cc'},
            {'hwaddr': '02:72:4e:0c:56:3d',
             'ip': '10.10.2.1',
             'name': 'sw2c1',
             'port': '02:8f:2e:cb:61:0f'},
            {'hwaddr': '02:60:73:65:59:eb',
             'ip': '10.10.3.1',
             'name': 'sw3c1',
             'port': '02:64:c3:6f:9b:5c'},
            {'hwaddr': '02:e3:28:62:92:38',
             'ip': '10.10.200.1',
             'name': 'sw-r-c1',
             'port': '02:e9:f6:e8:f5:e1'},
            {'hwaddr': '02:4c:af:86:3d:5b',
             'ip': '10.10.200.2',
             'name': 'sw-r-c2',
             'port': '02:5d:c9:b5:1c:17'},
            {'hwaddr': '02:50:82:d8:09:67',
             'ip': '10.10.200.3',
             'name': 'sw-r-c3',
             'port': '02:55:0c:51:b5:fc'},
            {'hwaddr': '02:3e:2d:ac:74:42',
             'ip': '10.10.200.4',
             'name': 'sw-r-c4',
             'port': '02:8f:37:f4:14:11'},
            {'cache': True,
             'hwaddr': '02:84:66:50:01:4c',
             'ip': '10.10.1.254',
             'name': 'sw1-cache1',
             'port': '02:82:f1:45:0e:7e'},
            {'cache': True,
             'hwaddr': '02:9a:93:0b:49:c3',
             'ip': '10.10.2.254',
             'name': 'sw2-cache1',
             'port': '02:43:25:81:93:c3'},
            {'cache': True,
             'hwaddr': '02:cf:d8:1e:1b:7f',
             'ip': '10.10.3.254',
             'name': 'sw3-cache1',
             'port': '02:95:68:76:bd:d3'}]

AvailableMPD = ["BigBuckBunny"]


def get_client_list():
    return [node["ip"] for node in NodeList]


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


def node_name_to_ip(name):
    for node in NodeList:
        if node["name"] == name:
            return node["ip"]


def ip_to_node_name(ip):
    for node in NodeList:
        if node["ip"] == ip:
            return node["name"]
