import networkx as nx
import random
import json
import os
import sys
from collections import defaultdict

# add project root directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_processing.config import DATA_PATHS

# load graph
try:
    G = nx.read_gexf(DATA_PATHS["graph_gexf"], node_type=str)
    print(f"Successfully loaded: {DATA_PATHS['graph_gexf']}")
    print(f"Graph contains {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
except FileNotFoundError:
    print(f"Graph file not found: {DATA_PATHS['graph_gexf']}")
    print("Please run the data processing pipeline to generate the graph file")
    sys.exit(1)
except Exception as e:
    print(f"Failed to load graph file: {e}")
    sys.exit(1)

# construct category -> skill mapping
category_skills = defaultdict(set)
valid_skills_in_graph = set()

for node, attr in G.nodes(data=True):
    # load skill information
    skills_raw = attr.get("skills", "")
    if isinstance(skills_raw, dict):
        skills_raw = skills_raw.get("value", "")
    skills = {s.strip() for s in str(skills_raw).split(",") if s.strip()}

    # load category information
    cat_raw = attr.get("categories", "")
    if isinstance(cat_raw, dict):
        cat_raw = cat_raw.get("value", "")
    categories = {c.strip() for c in str(cat_raw).split(",") if c.strip()}

    # establish mapping relationship
    for cat in categories:
        category_skills[cat].update(skills)

    valid_skills_in_graph.update(skills)

print(f"number of skills per category: {dict(sorted({k: len(v) for k, v in category_skills.items()}.items()))}")
print(f"number of valid skills in graph: {len(valid_skills_in_graph)}")

def generate_task(t, s):
    available_categories = list(category_skills.keys())
    if len(available_categories) < s:
        return None
    
    selected_categories = random.sample(available_categories, s)
    candidate_skills = set().union(*(category_skills[c] for c in selected_categories))
    candidate_skills = list(candidate_skills & valid_skills_in_graph)
    
    if len(candidate_skills) < t:
        return None
    
    sampled_skills = random.sample(candidate_skills, t)
    return {
        "t": t,
        "s": s,
        "skills": sampled_skills,
        "categories": selected_categories
    }

# follow the paper's method to generate tasks
tasks = []
random.seed(42)  # set random seed for reproducibility

for t in range(2, 21, 2):   # t ∈ {2, 4, ..., 20}
    for s in [1]:           # s = 1，use only one category
        generated = 0
        trials = 0
        print(f"generate t={t}, s={s} tasks")

        while generated < 100 and trials < 300:
            task = generate_task(t, s)
            if task:
                tasks.append(task)
                generated += 1
            trials += 1

        print(f"  {generated} tasks generated")

# ensure output directory exists
output_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
output_path = os.path.join(output_dir, "data", "evaluation", "generated_tasks.json")

os.makedirs(os.path.dirname(output_path), exist_ok=True)

# save tasks to file
with open(output_path, "w", encoding='utf-8') as f:
    json.dump(tasks, f, indent=2, ensure_ascii=False)

print(f"\nGenerated {len(tasks)} tasks, saved to: {output_path}")

# print statistics
task_stats = defaultdict(int)
for task in tasks:
    task_stats[task['t']] += 1

print("\nTask statistics:")
for t, count in sorted(task_stats.items()):
    print(f"  t={t}: {count} tasks")

# print example tasks
print("\nExample tasks:")
for i, task in enumerate(tasks[:5]):
    print(f"  Task {i+1}: t={task['t']}, s={task['s']}")
    print(f"  Skills: {task['skills']}")
    print(f"  Categories: {task['categories']}")
    print()
