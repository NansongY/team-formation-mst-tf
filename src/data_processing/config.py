import os

# project root directory
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# data paths configuration
DATA_PATHS = {
    "raw_papers": os.path.join(PROJECT_ROOT, "data", "raw", "papers-with-abstracts.json"),
    "filtered_papers": os.path.join(PROJECT_ROOT, "data", "processed", "filtered_papers.json"),
    "classified_papers": os.path.join(PROJECT_ROOT, "data", "processed", "filtered_papers_classified.json"),
    "author_skills": os.path.join(PROJECT_ROOT, "data", "processed", "author_skills.json"),
    "graph_gexf": os.path.join(PROJECT_ROOT, "data", "processed", "graph", "paperswithcode_graph_filtered.gexf"),
    "graph_png": os.path.join(PROJECT_ROOT, "data", "visualized", "paperswithcode_graph_filtered.png")
}

# category mapping configuration
CATEGORY_MAP = {
    "CV": ["CVPR", "ICCV", "ECCV"],
    "AI": ["AAAI", "NEURIPS", "ICLR"],
    "DM": ["KDD", "ICDM", "SDM", "PAKDD", "WWW"],
    "DB": ["SIGMOD", "VLDB", "ICDE", "EDBT"]
}

# processing parameters configuration
PROCESSING_CONFIG = {
    "min_papers_per_author": 3,
    "min_coauthor_papers": 2,
    "min_skill_frequency": 2,
}