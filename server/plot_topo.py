import json

import networkx as nx
from matplotlib import pyplot as plt
from networkx.readwrite import json_graph

data = '{"directed": false, "multigraph": false, "graph": {}, "nodes": [{"id": "sw2"}, {"id": "sw1"}, {"id": "cache1"}, {"id": "sw2c1"}, {"id": "sw2c2"}, {"id": "sw1c2"}, {"id": "sw1c1"}, {"id": "server"}], "links": [{"weight": 1.287, "source": "sw2", "target": "sw1"}, {"weight": 2.541, "source": "sw2", "target": "cache1"}, {"weight": 1.137, "source": "sw2", "target": "sw2c1"}, {"weight": 0.0, "source": "sw2", "target": "sw2c2"}, {"weight": 0.0, "source": "sw1", "target": "sw1c2"}, {"weight": 0.817, "source": "sw1", "target": "sw1c1"}, {"weight": 2.104, "source": "sw1", "target": "server"}]}'
res = json.loads(data)

H = json_graph.node_link_graph(res)
print(H)

pos = nx.planar_layout(H)
nx.draw(H, pos, with_labels=True)
labels = nx.get_edge_attributes(H, "weight")
print(labels)
nx.draw_networkx_edge_labels(H, pos, edge_labels=labels)
plt.show()
# plt.savefig("topo/topo-%s.png" % datetime.utcnow())
plt.close()
