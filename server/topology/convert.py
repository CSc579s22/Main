import xml.etree.ElementTree as ET

import networkx as nx
from matplotlib import pyplot as plt

tree = ET.parse('topo.xml')
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

pos = nx.spring_layout(G, seed=3)
nx.draw(G, pos, with_labels=True)
labels = nx.get_edge_attributes(G, "weight")
nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
plt.show()
plt.close()
