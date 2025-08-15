from collections import defaultdict
import networkx as nx
from .fast_steiner_tree import steiner_tree_graph

def enhance_graph_with_cliques(G, author_skills, T, D=1e9):
    H = nx.Graph()
    author_skill_map = dict()
    skill_nodes = set()
    clique_nodes_map = dict()      # author → [author::skill, ...]
    representative_node_map = {}   # author → representative node

    # Create author representative nodes (split by skill)
    for author, skills in author_skills.items():
        if author not in G:
            continue

        clique_nodes = [f"{author}::{skill}" for skill in skills]
        clique_nodes_map[author] = clique_nodes

        for node in clique_nodes:
            H.add_node(node)
            author_skill_map[node] = author

        # internal clique connections
        for i in range(len(clique_nodes)):
            for j in range(i + 1, len(clique_nodes)):
                H.add_edge(clique_nodes[i], clique_nodes[j], weight=0)

        # choose a representative node for the author
        if clique_nodes:
            representative_node_map[author] = clique_nodes[0]

    # construct sparse connections between representative nodes
    for u, v, data in G.edges(data=True):
        if u in representative_node_map and v in representative_node_map:
            rep_u = representative_node_map[u]
            rep_v = representative_node_map[v]
            weight = data.get("weight", 1.0)
            H.add_edge(rep_u, rep_v, weight=weight)

    # Add virtual skill nodes and connections 
    for skill in T:
        skill_node = f"skill::{skill}"
        H.add_node(skill_node)
        skill_nodes.add(skill_node)

        # iterate through authors and their skills, connecting to the skill node
        for author, skills in author_skills.items():
            if skill in skills:
                skill_specific_node = f"{author}::{skill}"
                if skill_specific_node in H:
                    H.add_edge(skill_node, skill_specific_node, weight=D)

    return H, skill_nodes, author_skill_map

def improved_enhance_steiner(G, author_skills, T):
    # Filter relevant authors (at least one target skill)
    relevant_authors = {
        author: skills for author, skills in author_skills.items() 
        if skills & T and author in G  # ensure author exists in the graph
    }
    
    if not relevant_authors:
        return set(), 0, False

    # Create enhanced graph H
    H, skill_nodes, author_skill_map = enhance_graph_with_cliques(G, relevant_authors, T)

    

    # check skill nodes connectivity
    connected_skill_nodes = set()
    for skill_node in skill_nodes:
        if H.degree(skill_node) > 0:
            connected_skill_nodes.add(skill_node)

    if not connected_skill_nodes:
        return set(), 0, False

    disconnected_skills = skill_nodes - connected_skill_nodes
    if disconnected_skills:
        print(f"Unconnected Skills: {[s.replace('skill::', '') for s in disconnected_skills]}")

    # Use Steiner Tree to cover connected skill nodes
    try:
        steiner_tree_subgraph = steiner_tree_graph(H, connected_skill_nodes)  
        steiner_nodes = set(steiner_tree_subgraph.nodes())
        
    except Exception as e:
        print(f"Steiner Tree failed: {e}")
        return set(), 0, False

    # Backtrack to find real authors
    team = {author_skill_map[node] for node in steiner_nodes if node in author_skill_map}

    # check if the team is connected
    if not team:
        return set(), 0, False
        
    subgraph = G.subgraph(team)
    is_connected = nx.is_connected(subgraph) if len(team) > 1 else True
    mst_cost = 0

    if is_connected and len(team) > 1:
        mst = nx.minimum_spanning_tree(subgraph, weight='weight')
        mst_cost = sum(data.get('weight', 1.0) for _, _, data in mst.edges(data=True))
    

    return team, mst_cost, is_connected