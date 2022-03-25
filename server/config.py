import sys

# Open vSwitch port status monitoring interval in seconds
Interval = 1
# MongoDB URI
MongoURI = "mongodb://mongo:27017/"
MaxInt = sys.maxsize

# Enable SABR cache server selection based on bandwidth estimation from SABR paper
EnableSABR = True

ConnectedSwitchPort = {'02:22:b6:3d:60:9b': '02:57:1f:9a:04:10',
                       '02:8c:12:70:7d:4e': '02:9a:17:bd:03:4f',
                       '02:d5:84:3f:5f:7c': '02:26:63:64:b4:7a',
                       '02:d8:85:9a:4f:13': '02:ca:2a:b6:62:27'}

Switch = [{'dpid': '00005a214fa04746',
           'name': 'sw1',
           'ports': [{'hwaddr': '02:b1:85:ea:a2:99',
                      'ip': '10.10.10.10',
                      'name': 'eth1'},
                     {'hwaddr': '02:64:ef:b1:d8:0e',
                      'ip': '10.10.10.12',
                      'name': 'eth2'},
                     {'hwaddr': '02:22:b6:3d:60:9b',
                      'ip': '10.10.10.2',
                      'name': 'eth3'}]},
          {'dpid': '00005a1bd227a14e',
           'name': 'sw2',
           'ports': [{'hwaddr': '02:d5:84:3f:5f:7c', 'ip': '10.10.10.4', 'name': 'eth1'},
                     {'hwaddr': '02:c0:73:be:04:5e',
                      'ip': '10.10.10.14',
                      'name': 'eth2'},
                     {'hwaddr': '02:24:17:7a:01:41',
                      'ip': '10.10.10.16',
                      'name': 'eth3'}]},
          {'dpid': '0000766d556b0749',
           'name': 'sw3',
           'ports': [{'hwaddr': '02:d8:85:9a:4f:13', 'ip': '10.10.10.6', 'name': 'eth1'},
                     {'hwaddr': '02:9d:57:9e:14:ed',
                      'ip': '10.10.10.20',
                      'name': 'eth2'},
                     {'hwaddr': '02:5b:dd:0e:e1:37',
                      'ip': '10.10.10.18',
                      'name': 'eth3'},
                     {'hwaddr': '02:9a:17:bd:03:4f',
                      'ip': '10.10.10.31',
                      'name': 'eth4'}]},
          {'dpid': '00007e2b97bdd241',
           'name': 'sw-r',
           'ports': [{'hwaddr': '02:17:71:fb:0d:bd',
                      'ip': '10.10.10.24',
                      'name': 'eth1'},
                     {'hwaddr': '02:6b:13:97:01:58',
                      'ip': '10.10.10.26',
                      'name': 'eth2'},
                     {'hwaddr': '02:26:62:42:52:4a',
                      'ip': '10.10.10.28',
                      'name': 'eth3'},
                     {'hwaddr': '02:00:ea:6c:fe:35',
                      'ip': '10.10.10.22',
                      'name': 'eth4'},
                     {'hwaddr': '02:8c:12:70:7d:4e',
                      'ip': '10.10.10.30',
                      'name': 'eth5'}]},
          {'dpid': '00008e604b2ec94c',
           'name': 'sw_origin',
           'ports': [{'hwaddr': '02:a1:af:dc:4c:f7', 'ip': '10.10.10.8', 'name': 'eth1'},
                     {'hwaddr': '02:57:1f:9a:04:10', 'ip': '10.10.10.3', 'name': 'eth2'},
                     {'hwaddr': '02:26:63:64:b4:7a', 'ip': '10.10.10.5', 'name': 'eth3'},
                     {'hwaddr': '02:ca:2a:b6:62:27',
                      'ip': '10.10.10.7',
                      'name': 'eth4'}]}]

NodeList = [{'hwaddr': '02:5a:46:59:d2:dc',
             'ip': '10.10.10.9',
             'name': 'server',
             'port': '02:a1:af:dc:4c:f7'},
            {'hwaddr': '02:5c:12:a3:6b:c2',
             'ip': '10.10.10.13',
             'name': 'sw1c1',
             'port': '02:64:ef:b1:d8:0e'},
            {'hwaddr': '02:fb:c2:bf:1f:51',
             'ip': '10.10.10.17',
             'name': 'sw2c1',
             'port': '02:24:17:7a:01:41'},
            {'hwaddr': '02:f0:d6:bf:04:78',
             'ip': '10.10.10.21',
             'name': 'sw3c1',
             'port': '02:9d:57:9e:14:ed'},
            {'hwaddr': '02:07:81:3d:dd:06',
             'ip': '10.10.10.23',
             'name': 'sw-r-c1',
             'port': '02:00:ea:6c:fe:35'},
            {'hwaddr': '02:1e:a6:48:85:c5',
             'ip': '10.10.10.25',
             'name': 'sw-r-c2',
             'port': '02:17:71:fb:0d:bd'},
            {'hwaddr': '02:f0:57:02:b2:b0',
             'ip': '10.10.10.27',
             'name': 'sw-r-c3',
             'port': '02:6b:13:97:01:58'},
            {'hwaddr': '02:0e:1b:3f:de:ab',
             'ip': '10.10.10.29',
             'name': 'sw-r-c4',
             'port': '02:26:62:42:52:4a'},
            {'cache': True,
             'hwaddr': '02:b6:aa:7a:f9:c1',
             'ip': '10.10.10.11',
             'name': 'sw1-cache1',
             'port': '02:b1:85:ea:a2:99'},
            {'cache': True,
             'hwaddr': '02:e9:b2:7b:89:1f',
             'ip': '10.10.10.15',
             'name': 'sw2-cache1',
             'port': '02:c0:73:be:04:5e'},
            {'cache': True,
             'hwaddr': '02:52:6a:d0:4d:87',
             'ip': '10.10.10.19',
             'name': 'sw3-cache1',
             'port': '02:5b:dd:0e:e1:37'}]

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
