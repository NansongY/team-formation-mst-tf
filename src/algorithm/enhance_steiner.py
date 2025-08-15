from collections import defaultdict
import networkx as nx
from .steiner_tree import steiner_tree_graph

def enhance_graph_with_cliques(G, author_skills, T, D=1e9):
    H = nx.Graph()
    author_rep_map = {}  # save author::skill → author mapping
    skill_nodes = set()
    author_clique_map = defaultdict(list)  # save each author's clique node list

    # Create author representative nodes (split by skill)
    for author, skills in author_skills.items():
        # create a clique for each author with their skills
        for skill in skills:
            node_name = f"author::{author}::{skill}"
            H.add_node(node_name)
            author_rep_map[node_name] = author
            author_clique_map[author].append(node_name)

    # Build clique internal connections (edge weight is 0)
    for author, nodes in author_clique_map.items():
        # Fully connect all nodes within the clique
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                H.add_edge(nodes[i], nodes[j], weight=0)

    # Inherit original graph edge structure
    for u, v, data in G.edges(data=True):
        weight = data.get("weight", 1.0)
        # Connect all clique nodes of the two authors
        for u_node in author_clique_map.get(u, []):
            for v_node in author_clique_map.get(v, []):
                H.add_edge(u_node, v_node, weight=weight)

    # Add virtual skill nodes and connections 
    for skill in T:
        skill_node = f"skill::{skill}"
        H.add_node(skill_node)
        skill_nodes.add(skill_node)

        # Connect all clique nodes of the two authors
        for author in author_skills:
            if skill in author_skills[author]:
                # Find the node corresponding to this skill for the author
                for node in author_clique_map[author]:
                    if node.endswith(f"::{skill}"):
                        H.add_edge(skill_node, node, weight=D)
    
    return H, skill_nodes, author_rep_map

def enhanced_steiner(G, author_skills, T):
    # Create enhanced graph H 
    H, skill_nodes, author_skill_map = enhance_graph_with_cliques(G, author_skills, T)

    # use Steiner Tree to cover skill nodes
    steiner_tree_subgraph = steiner_tree_graph(H, skill_nodes)  
    steiner_nodes = set(steiner_tree_subgraph.nodes())

    team = {author_skill_map[node] for node in steiner_nodes if node in author_skill_map}

    # check if the team is connected
    if not team:
        return set(), 0, False
        
    subgraph = G.subgraph(team)
    is_connected = nx.is_connected(subgraph) if len(team) > 1 else True
    mst_cost = 0

    if is_connected and len(team) > 1:
        mst = nx.minimum_spanning_tree(subgraph)
        mst_cost = sum(data['weight'] for _, _, data in mst.edges(data=True))

    return team, mst_cost, is_connected