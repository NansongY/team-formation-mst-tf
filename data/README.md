# Data Directory Structure

This directory contains the data files needed for the team formation algorithms. Due to privacy and size constraints, the raw dataset is not included in the repository.

## Directory Structure

```
data/
├── raw/
│   └── papers-with-abstracts.json    # Original paper dataset (not included)
├── processed/                        # Generated during data processing
│   ├── author_skills.json
│   ├── filtered_papers.json
│   ├── filtered_papers_classified.json
│   └── graph/
│       └── *.gexf                    # Network graph files
├── visualized/                       # Generated visualization files
│   └── *.png                        # Network and result visualizations
└── evaluation/
    └── generated_tasks.json          # Test tasks (included)
```

## Required Data Format

### papers-with-abstracts.json

The raw dataset should be a JSON array containing paper objects with the following structure:

```json
[
  {
    "title": "Paper Title",
    "authors": ["Author1", "Author2", "Author3"],
    "proceeding": "CONFERENCE_NAME YEAR",
    "tasks": ["task1", "task2", "task3"]
  }
]
```

### Data Requirements

- **title**: String containing the paper title
- **authors**: Array of author names (strings)
- **proceeding**: String containing conference/journal name and year
- **tasks**: Array of research tasks/skills (strings)

## Setup Instructions

1. Place your dataset file as `data/raw/papers-with-abstracts.json`
2. Run the data processing pipeline:
   ```bash
   python src/data_processing/data_process_pipeline.py
   ```
3. This will generate all processed files in the appropriate directories

## Notes

- The `processed/` and `visualized/` directories will be created automatically
- All generated files are excluded from git tracking
- The `evaluation/generated_tasks.json` file is included as it contains test parameters
