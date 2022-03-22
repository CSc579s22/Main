import networkx as nx
from config import MaxInt


def best_target_selection(graph, source, targets):
    print("===START best target selection===")
    paths = []
    for dst in targets:
        path = nx.shortest_paths.shortest_path(graph, source, dst)
        paths.append(path)

    weights = []
    for path in paths:
        print("path: ", path)
        i = 1
        min_weight = MaxInt
        while i < len(path)-1:
            weight = graph[path[i]][path[i+1]]["weight"]
            if weight < min_weight:
                min_weight = weight
            i += 1
        weights.append({"path": path, "min_weight": min_weight})

    best_path = []
    best_weight = 0
    for w in weights:
        if w["min_weight"] > best_weight:
            best_weight = w["min_weight"]
            best_path = w["path"]

    print("best path: ", best_path)
    print("best minimum bandwidth: ", best_weight)
    print("===END best target selection===")
    return best_path[len(best_path)-1]


if __name__ == "__main__":
    topo = nx.Graph()
    topo.add_node("server")
    topo.add_node("sw1")
    topo.add_node("sw1c1")
    topo.add_node("sw1c2")
    topo.add_node("sw2")
    topo.add_node("sw2c1")
    topo.add_node("sw2c2")
    topo.add_node("cache1")

    topo.add_edge("server", "sw1", weight=10)
    topo.add_edge("sw1c1", "sw1", weight=20)
    topo.add_edge("sw1c2", "sw1", weight=30)
    topo.add_edge("sw2", "sw1", weight=40)
    topo.add_edge("sw2", "sw2c1", weight=10)
    topo.add_edge("sw2", "cache1", weight=30)
    topo.add_edge("sw2", "sw2c2", weight=20)

    caches = ["server", "cache1"]
    src = "sw1c1"
    print(best_target_selection(topo, src, caches))
