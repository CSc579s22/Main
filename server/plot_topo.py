import json

import networkx as nx
from matplotlib import pyplot as plt
from networkx.readwrite import json_graph

data = '{"directed": false, "multigraph": false, "graph": {}, "nodes": [{"id": "sw-r"}, {"id": "sw-r-c3"}, {"id": "sw3"}, {"id": "sw-r-c4"}, {"id": "sw-r-c1"}, {"id": "sw-r-c2"}, {"id": "sw3c1"}, {"id": "sw_origin"}, {"id": "sw3-cache1"}, {"id": "sw1"}, {"id": "sw1-cache1"}, {"id": "sw1c1"}, {"id": "sw2"}, {"id": "sw2-cache1"}, {"id": "sw2c1"}], "links": [{"weight": 3.78, "source": "sw-r", "target": "sw-r-c3"}, {"weight": 18.956, "source": "sw-r", "target": "sw3"}, {"weight": 6.221, "source": "sw-r", "target": "sw-r-c4"}, {"weight": 4.481, "source": "sw-r", "target": "sw-r-c1"}, {"weight": 4.479, "source": "sw-r", "target": "sw-r-c2"}, {"weight": 0.0, "source": "sw3", "target": "sw3c1"}, {"weight": 5.507, "source": "sw3", "target": "sw_origin"}, {"weight": 24.464, "source": "sw3", "target": "sw3-cache1"}, {"weight": 0.0, "source": "sw_origin", "target": "sw1"}, {"weight": 0.0, "source": "sw_origin", "target": "sw2"}, {"weight": 0.0, "source": "sw1", "target": "sw1-cache1"}, {"weight": 0.0, "source": "sw1", "target": "sw1c1"}, {"weight": 0.0, "source": "sw2", "target": "sw2-cache1"}, {"weight": 0.0, "source": "sw2", "target": "sw2c1"}]}'
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
