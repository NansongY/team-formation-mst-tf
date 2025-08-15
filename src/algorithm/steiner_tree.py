import random
import networkx as nx

def steiner_tree(G, required_nodes, return_type='nodes'):
    
    if not required_nodes:
        return set() if return_type == 'nodes' else nx.Graph()
    
    T = nx.Graph()  # Initialize the Steiner tree graph
    # randomly select a starting node
    tree_nodes = set()
    current = random.choice(list(required_nodes))
    tree_nodes.add(current)

    uncovered = set(required_nodes)
    uncovered.remove(current)
    
    while uncovered:
        min_path = None
        min_weight = float('inf')

        # iterate through all pairs of nodes in the current tree
        for u in tree_nodes:
            for v in uncovered:
                try:
                    path = nx.shortest_path(G, source=u, target=v, weight='weight')
                    weight = nx.path_weight(G, path, weight='weight')
                    if weight < min_weight:
                        min_weight = weight
                        min_path = path
                except nx.NetworkXNoPath:
                    continue
        # if no path is found, break the loop
        if not min_path:
            break

        # add the minimum path to the Steiner tree
        for i in range(len(min_path) - 1):
            u, v = min_path[i], min_path[i + 1]
            weight = G[u][v]['weight']
            T.add_edge(u, v, weight=weight)
            tree_nodes.add(u)
            tree_nodes.add(v)

        uncovered = required_nodes - tree_nodes

    # return the Steiner tree as either a set of nodes or a subgraph
    if return_type == 'nodes':
        return tree_nodes
    elif return_type == 'graph':
        return T
    else:
        raise ValueError("return_type must be 'nodes' or 'graph'")

def steiner_tree_nodes(G, required_nodes):
    # Use the steiner_tree function to get nodes
    return steiner_tree(G, required_nodes, return_type='nodes')

def steiner_tree_graph(G, required_nodes):
    # Use the steiner_tree function to get the subgraph
    return steiner_tree(G, required_nodes, return_type='graph')