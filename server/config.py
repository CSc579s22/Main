import sys

# Open vSwitch port status monitoring interval in seconds
Interval = 1
# Queue size to store previous stats
QueueSize = 10
# MongoDB URI
MongoURI = "mongodb://mongo:27017/"
MaxInt = sys.maxsize

# Enable SABR cache server selection based on bandwidth estimation from SABR paper
EnableSABR = True

ConnectedSwitchPort = {'02:39:fe:fd:b7:6f': '02:50:e3:d5:03:64',
                       '02:3c:58:25:27:45': '02:cd:0a:2e:64:c8',
                       '02:7e:a6:b9:a4:95': '02:64:60:07:71:93',
                       '02:a4:e5:8f:73:0e': '02:1d:f4:c3:bb:0e'}

Switch = [{'dpid': '000096472e9e0648',
           'name': 'sw1',
           'ports': [{'hwaddr': '02:d1:bd:09:9d:b4', 'ip': '10.10.10.9', 'name': 'eth1'},
                     {'hwaddr': '02:5b:3d:94:17:8e',
                      'ip': '10.10.10.11',
                      'name': 'eth2'},
                     {'hwaddr': '02:39:fe:fd:b7:6f',
                      'ip': '10.10.10.2',
                      'name': 'eth3'}]},
          {'dpid': '0000b623e0b4ef43',
           'name': 'sw2',
           'ports': [{'hwaddr': '02:11:48:db:cc:2c',
                      'ip': '10.10.10.13',
                      'name': 'eth1'},
                     {'hwaddr': '02:3b:81:81:3c:51',
                      'ip': '10.10.10.15',
                      'name': 'eth2'},
                     {'hwaddr': '02:a4:e5:8f:73:0e',
                      'ip': '10.10.10.4',
                      'name': 'eth3'}]},
          {'dpid': '0000bac243952b46',
           'name': 'sw3',
           'ports': [{'hwaddr': '02:7e:a6:b9:a4:95', 'ip': '10.10.10.6', 'name': 'eth1'},
                     {'hwaddr': '02:cd:0a:2e:64:c8',
                      'ip': '10.10.10.30',
                      'name': 'eth2'},
                     {'hwaddr': '02:93:57:8d:41:00',
                      'ip': '10.10.10.17',
                      'name': 'eth3'},
                     {'hwaddr': '02:7f:4c:17:46:03',
                      'ip': '10.10.10.19',
                      'name': 'eth4'}]},
          {'dpid': '00004a5d6b04044d',
           'name': 'sw-r',
           'ports': [{'hwaddr': '02:3c:58:25:27:45',
                      'ip': '10.10.10.29',
                      'name': 'eth1'},
                     {'hwaddr': '02:e7:f2:32:f8:58',
                      'ip': '10.10.10.21',
                      'name': 'eth2'},
                     {'hwaddr': '02:8b:71:1c:ea:6c',
                      'ip': '10.10.10.23',
                      'name': 'eth3'},
                     {'hwaddr': '02:99:75:bb:da:24',
                      'ip': '10.10.10.25',
                      'name': 'eth4'},
                     {'hwaddr': '02:76:b5:19:97:be',
                      'ip': '10.10.10.27',
                      'name': 'eth5'}]},
          {'dpid': '00009a0f13988b48',
           'name': 'sw_origin',
           'ports': [{'hwaddr': '02:1d:f4:c3:bb:0e', 'ip': '10.10.10.5', 'name': 'eth1'},
                     {'hwaddr': '02:64:60:07:71:93', 'ip': '10.10.10.7', 'name': 'eth2'},
                     {'hwaddr': '02:bf:1f:1a:d5:26', 'ip': '10.10.10.8', 'name': 'eth3'},
                     {'hwaddr': '02:50:e3:d5:03:64',
                      'ip': '10.10.10.3',
                      'name': 'eth4'}]}]

NodeList = [{'hwaddr': '02:6d:28:4b:16:a6',
             'ip': '10.10.10.1',
             'name': 'server',
             'port': '02:05:f3:7e:a9:36'},
            {'hwaddr': '02:03:dd:8e:cf:75',
             'ip': '10.10.10.10',
             'name': 'sw1c1',
             'port': '02:5c:9a:c9:72:e4'},
            {'hwaddr': '02:ff:c8:38:3c:60',
             'ip': '10.10.10.12',
             'name': 'sw1c2',
             'port': '02:3d:1f:da:5f:18'},
            {'hwaddr': '02:64:30:5a:83:af',
             'ip': '10.10.10.14',
             'name': 'sw1c3',
             'port': '02:55:f4:f0:f7:ae'},
            {'hwaddr': '02:cb:8e:3a:c5:86',
             'ip': '10.10.10.16',
             'name': 'sw1c4',
             'port': '02:5d:d5:2b:3a:29'},
            {'hwaddr': '02:56:78:e7:2b:54',
             'ip': '10.10.10.20',
             'name': 'sw2c1',
             'port': '02:b0:b8:5c:7e:12'},
            {'hwaddr': '02:3b:8e:5a:77:78',
             'ip': '10.10.10.22',
             'name': 'sw2c2',
             'port': '02:58:65:f1:54:b6'},
            {'hwaddr': '02:96:d3:0e:88:dd',
             'ip': '10.10.10.24',
             'name': 'sw2c3',
             'port': '02:a5:6f:e0:e0:ab'},
            {'hwaddr': '02:34:bf:82:98:89',
             'ip': '10.10.10.26',
             'name': 'sw2c4',
             'port': '02:d2:ad:49:1f:3b'},
            {'cache': True,
             'hwaddr': '02:6b:0f:3a:25:e0',
             'ip': '10.10.10.8',
             'name': 'sw1-cache1',
             'port': '02:3e:6a:af:85:ff'},
            {'cache': True,
             'hwaddr': '02:8a:3a:ff:fd:31',
             'ip': '10.10.10.18',
             'name': 'sw2-cache1',
             'port': '02:94:f9:b0:1d:ee'}]

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
