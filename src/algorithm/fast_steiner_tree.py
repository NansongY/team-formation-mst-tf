import networkx as nx
import random

def steiner_tree(G, required_nodes, return_type='nodes'):
    
    if not required_nodes:
        return set() if return_type == 'nodes' else nx.Graph()

    # randomly select a starting node
    tree_nodes = set()
    current = random.choice(list(required_nodes))
    tree_nodes.add(current)

    uncovered = set(required_nodes)
    uncovered.remove(current)

    # greedy approach to connect the nearest uncovered nodes
    while uncovered:
        best_path = None
        best_length = float('inf')

        # find the shortest path from any uncovered node to any node in the tree
        for u in uncovered:
            try:
                for t in tree_nodes:
                    path = nx.shortest_path(G, source=u, target=t, weight="weight")
                    length = nx.path_weight(G, path, weight="weight")
                    if length < best_length:
                        best_length = length
                        best_path = path
            except nx.NetworkXNoPath:
                continue

        if best_path is None:
            print(f" Warning: Cannot connect to node(s): {uncovered}")
            break

        # add nodes in the best path to the tree
        tree_nodes.update(best_path)
        uncovered -= set(best_path)  # remove covered nodes

    # return the result based on the return type
    if return_type == 'nodes':
        return tree_nodes
    elif return_type == 'graph':
        # construct a subgraph containing all tree nodes
        T = G.subgraph(tree_nodes).copy()
        return T
    else:
        raise ValueError("return_type must be 'nodes' or 'graph'")

def steiner_tree_nodes(G, required_nodes):
    # Use the steiner_tree function to get nodes
    return steiner_tree(G, required_nodes, return_type='nodes')

def steiner_tree_graph(G, required_nodes):
    # Use the steiner_tree function to get the subgraph
    return steiner_tree(G, required_nodes, return_type='graph')