import networkx as nx
from collections import defaultdict
from .steiner_tree import steiner_tree_nodes

def greedy_cover(author_skills, T):
   
    # Initialize
    covered_skills = set()  # covered skills as set
    team = set()            # final team
    
    # Add authors who have skills
    skill_authors = defaultdict(set)
    for author, skills in author_skills.items():
        for skill in skills:
            if skill in T:  # focus on needed skills
                skill_authors[skill].add(author)
    
    # Keep iterating if skills are not fully covered
    while covered_skills != T:
        best_author = None
        best_new_skills = set()
        
        # find author who covered most new skills
        for author, skills in author_skills.items():
            if author in team:  # skip the chosen
                continue
                
            new_skills = (skills & T) - covered_skills  # new skills from authors
            
            # update the better choices of skill
            if len(new_skills) > len(best_new_skills):
                best_author = author
                best_new_skills = new_skills
        
        # If no appropriate author, exit
        if best_author is None:
            print(f"Cannot cover skills: {T - covered_skills}")
            break
        
        # add author and update the skills
        team.add(best_author)
        covered_skills |= best_new_skills
    
    return team

def cover_steiner(G, author_skills, T):

    # Greedy cover
    X0 = greedy_cover(author_skills, T)
    
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