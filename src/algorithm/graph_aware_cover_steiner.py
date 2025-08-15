import networkx as nx
from collections import defaultdict
from .steiner_tree import steiner_tree_nodes

def graph_aware_greedy_cover(G, author_skills, T, current_team=set()):
    covered_skills = set()
    team = set(current_team)
    
    # compute center of the current team
    center = None
    if team:
        center = min(team, key=lambda a: sum(
            nx.shortest_path_length(G, source=a, target=b, weight='weight') 
            for b in team
        ))
    
    while covered_skills != T:
        best_author = None
        best_score = -float('inf')
        
        for author, skills in author_skills.items():
            if author in team:
                continue
                
            new_skills = (skills & T) - covered_skills
            if not new_skills:
                continue
                
            # compute connection cost to the center
            connection_cost = 0
            if center:
                try:
                    connection_cost = nx.shortest_path_length(G, source=author, target=center, weight='weight')
                except nx.NetworkXNoPath:
                    connection_cost = float('inf')
            
            # total score is a combination of new skills and connection cost
            coverage_score = len(new_skills)
            connection_score = 1 / (connection_cost + 1)  # avoid division by zero
            total_score = coverage_score * connection_score
            
            if total_score > best_score:
                best_author = author
                best_score = total_score
                best_new_skills = new_skills
        
        if best_author is None:
            break
            
        team.add(best_author)
        covered_skills |= best_new_skills
        # update center to the newly added author
        center = best_author
    
    return team

def graph_aware_cover_steiner(G, author_skills, T):

    # Greedy cover
    X0 = graph_aware_greedy_cover(G, author_skills, T)
    
    # SteinerTree
    team = steiner_tree_nodes(G, X0) 
    
    # Communication cost
    subgraph = G.subgraph(team)
    is_connected = nx.is_connected(subgraph)
    mst_cost = 0
    
    if is_connected:
        mst = nx.minimum_spanning_tree(subgraph)
        mst_cost = sum(data['weight'] for _, _, data in mst.edges(data=True))
    else:
        print("Team members are not connected, unable to compute mst cost")
    
    return team, mst_cost, is_connected