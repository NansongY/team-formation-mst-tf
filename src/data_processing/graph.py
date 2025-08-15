import json
import re
import itertools
import networkx as nx
import matplotlib.pyplot as plt
from collections import defaultdict, Counter
from config import CATEGORY_MAP, DATA_PATHS, PROCESSING_CONFIG

def load_classified_papers():
    # Load classified papers from the specified path
    with open(DATA_PATHS["classified_papers"], "r", encoding="utf-8") as f:
        return json.load(f)

def build_author_data(papers):
    # Build author data structure
    author_papers = defaultdict(set)
    author_categories = defaultdict(set)
    
    for paper in papers:
        title = paper.get("title", "")
        proceeding = paper.get("proceeding", "").upper()
        authors = paper.get("authors", [])
        
        matched_category = None
        for cat, keywords in CATEGORY_MAP.items():
            if any(p in proceeding for p in keywords):
                matched_category = cat
                break
        
        for author in authors:
            author_papers[author].add(title)
            if matched_category:
                author_categories[author].add(matched_category)
    
    return author_papers, author_categories

def filter_active_authors(author_papers, min_papers=None):
    # Filter active authors (number of papers >= threshold)
    if min_papers is None:
        min_papers = PROCESSING_CONFIG["min_papers_per_author"]
    
    filtered_authors = {a for a, titles in author_papers.items() if len(titles) >= min_papers}
    print(f"Active authors (>= {min_papers} papers): {len(filtered_authors)}")
    return filtered_authors

def extract_author_skills_from_tasks(filtered_authors, papers):
    # Extract author skills from the tasks field of papers
    min_frequency = PROCESSING_CONFIG["min_skill_frequency"]
    
    # Build author-task mapping
    author_task_counter = defaultdict(Counter)

    # Count occurrences of each task for each author
    for paper in papers:
        authors = paper.get("authors", [])
        tasks = paper.get("tasks", [])
        
        for author in authors:
            if author in filtered_authors:  # active authors only
                for task in tasks:
                    if task:  # ensure task is not empty
                        # Normalize task name
                        # Remove brackets and their contents (including () [] {})
                        normalized_task = re.sub(r'[\(\[\{][^\)\]\}]*[\)\]\}]', '', task.strip())
                        # Replace punctuation with spaces
                        normalized_task = re.sub(r'[^\w\s]', ' ', normalized_task)
                        # Merge multiple consecutive spaces into a single space
                        normalized_task = re.sub(r'\s+', ' ', normalized_task)
                        # Convert to lowercase and strip leading/trailing spaces
                        normalized_task = normalized_task.lower().strip()
                        if normalized_task:
                            author_task_counter[author][normalized_task] += 1
    
    # construct author skills set
    author_skills = {}
    for author in filtered_authors:
        skills = set()
        for task, count in author_task_counter[author].items():
            if count >= min_frequency:
                skills.add(task)
        
        if skills:  # remove authors with no skills
            author_skills[author] = skills

    print(f"skills extracted for {len(author_skills)} authors")

    # Print skill statistics
    all_skills = set()
    for skills in author_skills.values():
        all_skills.update(skills)
    print(f"total {len(all_skills)} unique skills extracted")

    # Print most common skills
    skill_frequency = Counter()
    for skills in author_skills.values():
        for skill in skills:
            skill_frequency[skill] += 1

    print("10 most common skills:")
    for skill, count in skill_frequency.most_common(10):
        print(f"  - {skill}: {count} authors")

    return author_skills

def save_author_skills(author_skills):
    # Save author skills to JSON file
    author_skills_json = {author: list(skills) for author, skills in author_skills.items()}
    with open(DATA_PATHS["author_skills"], "w", encoding="utf-8") as f:
        json.dump(author_skills_json, f, indent=2, ensure_ascii=False)
    print(f"Author skills saved to {DATA_PATHS['author_skills']}")

def build_collaboration_graph(author_skills, author_papers, author_categories):
    # Build the co-authorship graph
    min_coauthor_papers = PROCESSING_CONFIG["min_coauthor_papers"]
    
    G = nx.Graph()
    G.add_nodes_from(author_skills.keys())
    
    edges_added = 0
    example_edges = []
    
    # Calculate Jaccard distance between authors based on shared papers
    for a1, a2 in itertools.combinations(author_skills.keys(), 2):
        papers1 = author_papers[a1]
        papers2 = author_papers[a2]
        common_papers = papers1 & papers2
        
        if len(common_papers) >= min_coauthor_papers:
            jaccard_dist = 1 - len(papers1 & papers2) / len(papers1 | papers2)
            G.add_edge(a1, a2, weight=jaccard_dist)
            edges_added += 1
            
            if len(example_edges) < 5:
                example_edges.append((a1, a2, round(jaccard_dist, 3)))

    # Add node attributes
    for author in G.nodes():
        G.nodes[author]["num_skills"] = len(author_skills[author])
        G.nodes[author]["skills"] = ", ".join(sorted(author_skills[author]))
        G.nodes[author]["categories"] = ", ".join(sorted(author_categories.get(author, set())))

    print(f"edges added: {edges_added}")
    print(f"example edges: ")
    for a, b, w in example_edges:
        print(f"   - {a} ↔ {b} | Jaccard distance = {w}")

    return G

def save_graph(G):
    # Save graph data and visualization
    # Save GEXF format
    nx.write_gexf(G, DATA_PATHS["graph_gexf"])

    # Generate visualization
    plt.figure(figsize=(12, 8))
    nx.draw(G, node_size=30, edge_color="gray", alpha=0.3, with_labels=False)
    plt.title(f"Author Collaboration Network (>={PROCESSING_CONFIG['min_coauthor_papers']} co-authored papers)")
    plt.axis("off")
    plt.savefig(DATA_PATHS["graph_png"], dpi=300, bbox_inches='tight')
    plt.close()

    print(f"Graph data saved to: {DATA_PATHS['graph_gexf']}")
    print(f"Visualization saved to: {DATA_PATHS['graph_png']}")

def main():
    # Main function to build the author collaboration network
    print("Starting to build author collaboration network...")

    # Load data
    papers = load_classified_papers()
    print(f"Loaded {len(papers)} classified papers")

    # Build author data
    author_papers, author_categories = build_author_data(papers)
    print(f"Found {len(author_papers)} authors")

    # Filter active authors
    filtered_authors = filter_active_authors(author_papers)

    # Extract skills from tasks field
    author_skills = extract_author_skills_from_tasks(filtered_authors, papers)
    save_author_skills(author_skills)

    # Build graph
    G = build_collaboration_graph(author_skills, author_papers, author_categories)
    save_graph(G)

    print(f"Network statistics: {G.number_of_nodes()} nodes (authors), {G.number_of_edges()} edges (collaborations)")

    return G

if __name__ == "__main__":
    main()