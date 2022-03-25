import xml.etree.ElementTree as ET

import networkx as nx
from matplotlib import pyplot as plt
from config import switch
from server.config import Switch


def get_nx_graph_from_xml(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    G = nx.Graph()
    node_link_map = {}
    for node in root:
        if str.endswith(node.tag, "node"):
            G.add_node(node.attrib["client_id"])
            node_dict = {"interface": []}
            for iface in node:
                if str.endswith(iface.tag, "interface"):
                    node_dict["interface"].append(iface.attrib["client_id"])
                    node_link_map[iface.attrib["client_id"]] = node.attrib["client_id"]
    for link in root:
        if str.endswith(link.tag, "link"):
            ref = []
            for l in link:
                if str.endswith(l.tag, "interface_ref"):
                    ref.append(l.attrib["client_id"])
            assert len(ref) == 2
            G.add_edge(node_link_map[ref[0]], node_link_map[ref[1]])
    return G


def get_node_port_ip_on_sw(filename, node_name, ip):
    tree = ET.parse(filename)
    root = tree.getroot()
    ifname = ""
    for node in root:
        if str.endswith(node.tag, "node"):
            if node.attrib["client_id"] == node_name:
                for iface in node:
                    if str.endswith(iface.tag, "interface"):
                        for i in iface:
                            if str.endswith(i.tag, "ip"):
                                if i.attrib["address"] == ip:
                                    ifname = iface.attrib["client_id"]
                                    break
    # print(ifname)
    port_iface_name = ""
    for link in root:
        """
        <link client_id="link-sw2-cache1">
            <interface_ref client_id="sw2:if-sw2-cache1"/>
            <interface_ref client_id="sw2-cache1:if-cache1-sw2"/>
            <jacks:site id="multilayer"/>
        </link>
        """
        if str.endswith(link.tag, "link"):
            ref = []
            for l in link:
                if str.endswith(l.tag, "interface_ref"):
                    ref.append(l.attrib["client_id"])
            assert len(ref) == 2
            if ref[0] == ifname:
                port_iface_name = ref[1]
                break
            if ref[1] == ifname:
                port_iface_name = ref[0]
                break
    # print(port_iface_name)
    for node in root:
        if str.endswith(node.tag, "node"):
            for iface in node:
                if str.endswith(iface.tag, "interface"):
                    if iface.attrib["client_id"] == port_iface_name:
                        for i in iface:
                            if str.endswith(i.tag, "ip"):
                                port_ip = i.attrib["address"]
                                return node.attrib["client_id"], port_ip


def get_mac_by_ip_from_config(ip):
    for i in range(len(Switch)):
        for port_i in Switch[i]["ports"]:
            if port_i["ip"] == ip:
                return port_i["hwaddr"]


def get_connected_sw_mapping(filename):
    ConnectedSWKeys = {}
    tree = ET.parse(filename)
    root = tree.getroot()
    interface_ip_mapping = {}
    sw_list = [sw["name"] for sw in switch]
    for node in root:
        if str.endswith(node.tag, "node"):
            for iface in node:
                if str.endswith(iface.tag, "interface"):
                    for ip in iface:
                        if str.endswith(ip.tag, "ip"):
                            interface_ip_mapping[iface.attrib["client_id"]] = ip.attrib["address"]
    for link in root:
        if str.endswith(link.tag, "link"):
            ref = []
            for l in link:
                if str.endswith(l.tag, "interface_ref"):
                    ref.append(l.attrib["client_id"])
            assert len(ref) == 2
            if ref[0].split(":")[0] in sw_list and ref[1].split(":")[0] in sw_list:
                ip1 = interface_ip_mapping[ref[0]]
                ip2 = interface_ip_mapping[ref[1]]
                hwaddr1 = get_mac_by_ip_from_config(ip1)
                hwaddr2 = get_mac_by_ip_from_config(ip2)
                ConnectedSWKeys[hwaddr1] = hwaddr2
    return ConnectedSWKeys


if __name__ == "__main__":
    G = get_nx_graph_from_xml("topo.xml")
    pos = nx.spring_layout(G, seed=3)
    nx.draw(G, pos, with_labels=True)
    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()
    plt.close()
