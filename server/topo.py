import networkx as nx
import matplotlib.pyplot as plt


def load_topo():
    print("load topo")


topo = nx.Graph()
topo.add_node("server")
topo.add_edge("server", "1")
# topo.add_node("sw1")
# topo.add_node("sw2")
# topo.add_node("sw1c1")
# topo.add_node("sw1c2")
# topo.add_node("sw2c1")
# topo.add_node("sw2c2")
# topo.add_node("cache1")
# topo.add_edge("server", "sw1", weight=10)
# topo.add_edge("sw1c1", "sw1", weight=20)
# topo.add_edge("sw1c2", "sw1", weight=30)
# topo.add_edge("sw1", "sw2", weight=40)
# topo.add_edge("sw2c1", "sw2", weight=10)
# topo.add_edge("sw2c2", "sw2", weight=20)
# topo.add_edge("cache1", "sw2", weight=30)

pos = nx.spring_layout(topo)
nx.draw(topo, pos, with_labels=True)
labels = nx.get_edge_attributes(topo, "weight")
nx.draw_networkx_edge_labels(topo, pos, edge_labels=labels)
plt.show()


# path = nx.shortest_paths.shortest_path(topo, "sw1c1", "sw2c2")
# print(path)
#
# print(topo.has_node("sw1"))
# print(topo.has_node("1.2.3.4"))
