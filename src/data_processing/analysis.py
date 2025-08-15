import json
from config import CATEGORY_MAP, DATA_PATHS

def load_filtered_papers():
    # load the filtered papers from the specified path
    with open(DATA_PATHS["filtered_papers"], "r", encoding="utf-8") as f:
        return json.load(f)

def create_category_mapping():
    # Create a mapping from conference names to categories
    conf_to_category = {}
    for cat, confs in CATEGORY_MAP.items():
        for conf in confs:
            conf_to_category[conf.upper()] = cat
    return conf_to_category

def classify_papers(papers, conf_to_category):
    # Classify papers based on their proceeding information
    classified_papers = []
    for paper in papers:
        raw_proceeding = paper.get("proceeding", "")
        conf_abbr = raw_proceeding.strip().split()[0].upper()
        category = conf_to_category.get(conf_abbr)
        
        if category:
            paper["proceeding"] = conf_abbr
            paper["category"] = category
            classified_papers.append(paper)
    
    return classified_papers

def save_classified_papers(classified_papers):
    # Save the classified papers to the specified path
    with open(DATA_PATHS["classified_papers"], "w", encoding="utf-8") as f:
        json.dump(classified_papers, f, indent=2, ensure_ascii=False)
    print(f"saved {len(classified_papers)} papers to {DATA_PATHS['classified_papers']}")

def main():
    # Main analysis process
    print("starting paper classification...")
    papers = load_filtered_papers()
    conf_to_category = create_category_mapping()
    
    classified_papers = classify_papers(papers, conf_to_category)
    save_classified_papers(classified_papers)

    print(f"Classification complete, retained {len(classified_papers)} papers in CV/AI/DM/DB categories")
    return classified_papers

if __name__ == "__main__":
    main()
