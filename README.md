# Team Formation using Steiner Tree (MST-TF)

A research project implementing team formation algorithms based on author collaboration networks and skill requirements.

## Project Structure

```
team-formation-mst-tf/
├── data/
|   ├── evaluation/
|   |   ├── generated_tasks.json               # Generated task
│   ├── raw/
│   │   └── papers-with-abstracts.json         # Original paper dataset
│   ├── processed/
│   │   ├── author_skills.json                 # Extracted author skills
│   │   ├── filtered_papers.json               # Filtered papers
│   │   ├── filtered_papers_classified.json    # Classified papers
│   │   └── graph/
│   │       ├── paperswithcode_graph_filtered.gexf  # Author collaboration network
│   │       └── *_team_subgraph.gexf           # Algorithm result graphs
│   └── visualized/
│       ├── paperswithcode_graph_filtered.png            # Network visualization
│       └── *_team_subgraph.png                # Team visualizations
├── src/
│   ├── algorithm/
│   │   ├── steiner_tree.py                    # Core Steiner Tree algorithm
│   │   ├── cover_steiner.py                   # CoverSteiner algorithm
│   │   ├── graph_aware_cover_steiner.py       # Graph aware CoverSteiner algorithm
│   │   └── enhance_steiner.py                 # EnhancedSteiner algorithm
│   ├── data_processing/
│   │   ├── config.py                          # Configuration settings
│   │   ├── raw_data_processing.py             # Raw data processing
│   │   ├── analysis.py                        # Paper classification
│   │   ├── graph.py                           # Network construction
│   │   └── data_process_pipeline.py           # Complete pipeline
│   └── evaluator/
|       ├── evaluation.py                      # Evaluation test
│       └── task_generator.py                  # Test task generation
└── test_algorithms.py                         # Algorithm testing tool
```

## Quick Start

### 1. Prepare Data
Place your dataset file as `data/raw/papers-with-abstracts.json`. See [`data/README.md`](data/README.md) for the required data format.

### 2. Data Processing
```bash
# Process raw data and build collaboration network
python src/data_processing/data_process_pipeline.py
```

### 3. Algorithm Testing
```bash
# Test all algorithms
python test_algorithms.py

# Test specific algorithm
python test_algorithms.py cover_steiner
python test_algorithms.py enhance_steiner

# Test multiple algorithms
python test_algorithms.py cover_steiner enhance_steiner
```

## Algorithms

- **CoverSteiner**: Greedy skill coverage + Steiner Tree approach
- **EnhancedSteiner**: Enhanced graph with author-skill cliques + Steiner Tree

## Data Flow

1. **Raw Papers** → Filter & Classify → **Processed Papers**
2. **Author Skills** → Extract from paper tasks → **Skill Database**
3. **Collaboration Network** → Build from co-authorship → **Graph Structure**
4. **Team Formation** → Apply algorithms → **Optimal Teams**

## Output

- Team collaboration subgraphs (GEXF format)
- Team visualizations (PNG format)
- Algorithm performance metrics
- Execution time comparisons

## Requirements

- Python 3.8+
- NetworkX
- Matplotlib
- NumPy
- JSON

## Data Requirements

The project requires a dataset in JSON format containing academic papers with:
- Paper titles and authors
- Conference/journal proceedings
- Research tasks/skills

See [`data/README.md`](data/README.md) for detailed format specifications.

## Research Focus

This project focuses on finding optimal research teams by:
- Modeling author collaboration as weighted graphs
- Extracting skills from research paper tasks
- Applying graph-theoretic algorithms for team formation
- Minimizing communication costs while covering required skills
