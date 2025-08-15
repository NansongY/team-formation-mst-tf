import json
from config import DATA_PATHS

def load_raw_data():
    # Load raw papers data from the specified path
    with open(DATA_PATHS["raw_papers"], "r", encoding="utf-8") as f:
        return json.load(f)

def filter_papers(raw_data):
    # Filter papers that contain proceeding information
    filtered_data = []
    for paper in raw_data:
        if paper.get("proceeding"):
            filtered_data.append({
                "title": paper["title"],
                "authors": paper["authors"],
                "proceeding": paper["proceeding"],
                "tasks": paper["tasks"]
            })
    return filtered_data

def save_filtered_papers(filtered_data):
    # Save filtered papers data
    with open(DATA_PATHS["filtered_papers"], "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(filtered_data)} papers to {DATA_PATHS['filtered_papers']}")

def main():
    """Main processing flow"""
    print("Starting to process raw data...")
    raw_data = load_raw_data()
    print(f"Loaded {len(raw_data)} raw papers")

    filtered_data = filter_papers(raw_data)
    save_filtered_papers(filtered_data)
    
    return filtered_data

if __name__ == "__main__":
    main()
