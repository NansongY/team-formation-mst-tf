import json
import networkx as nx
import matplotlib.pyplot as plt
import os
import sys
import argparse
import time

# 添加src目录到路径，以便导入模块
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "src"))

from algorithm.cover_steiner import cover_steiner
from algorithm.enhance_steiner import enhanced_steiner
from algorithm.graph_aware_cover_steiner import graph_aware_cover_steiner
from algorithm.improved_enhance_steiner import improved_enhance_steiner
from data_processing.config import DATA_PATHS

def load_data():
    G = nx.read_gexf(DATA_PATHS["graph_gexf"], node_type=str)

    # normalize node names to UTF-8 to avoid encoding issues
    node_mapping = {node: node.encode('utf-8').decode('utf-8') for node in G.nodes()}
    G = nx.relabel_nodes(G, node_mapping)

    # load author skills with specified encoding
    with open(DATA_PATHS["author_skills"], encoding='utf-8') as f:
        author_skills_raw = json.load(f)
        author_skills = {
            author.encode('utf-8').decode('utf-8'): set(skills) if isinstance(skills, list) else skills
            for author, skills in author_skills_raw.items()
        }
    
    return G, author_skills

def visualize_team(G, team, author_skills, sample_task, algorithm_name, output_dir):
    # visualize the team subgraph
    if not team:
        print(f" {algorithm_name} see no team members to visualize.")
        return
    
    team_subgraph = G.subgraph(team)

    # save GEXF file
    gexf_path = os.path.join(output_dir["graph"], f"{algorithm_name}_team_subgraph.gexf")
    nx.write_gexf(team_subgraph, gexf_path)

    # generate visualization
    plt.figure(figsize=(12, 8))
    
    if team_subgraph.number_of_nodes() == 0:
        plt.text(0.5, 0.5, f"{algorithm_name}\nsee no team members", 
                ha='center', va='center', fontsize=16)
        plt.xlim(0, 1)
        plt.ylim(0, 1)
    else:
        pos = nx.spring_layout(team_subgraph, seed=42)

        # draw edges and nodes
        nx.draw_networkx_edges(team_subgraph, pos, edge_color='gray', width=1, alpha=0.7)
        nx.draw_networkx_nodes(team_subgraph, pos, node_color='lightblue', node_size=300)

        # add author name labels
        nx.draw_networkx_labels(team_subgraph, pos, font_size=6)

        # add skill labels (only show relevant skills)
        pos_attrs = {}
        for node in team_subgraph.nodes():
            pos_attrs[node] = (pos[node][0], pos[node][1] - 0.06)
            
        skills_labels = {}
        for node in team_subgraph.nodes():
            if node in author_skills:
                relevant_skills = author_skills[node] & sample_task
                if relevant_skills:
                    skills_labels[node] = ',\n'.join(list(relevant_skills)[:3])  # at most 3 skills per author

        if skills_labels:
            nx.draw_networkx_labels(team_subgraph, pos_attrs, skills_labels,
                                  font_size=4, font_color='red')
    
    plt.title(f"{algorithm_name} team subgraph", pad=20)
    plt.axis('off')
    plt.tight_layout()

    # 保存PNG文件
    png_path = os.path.join(output_dir["visualized"], f"{algorithm_name}_team_subgraph.png")
    plt.savefig(png_path, dpi=300, bbox_inches='tight')
    plt.close()

    print(f" saved gexf: {gexf_path}")
    print(f" saved visualization: {png_path}")

def ensure_directories():
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    output_dirs = {
        "graph": os.path.join(project_root, "data", "processed", "graph"),
        "visualized": os.path.join(project_root, "data", "visualized")
    }
    
    for dir_path in output_dirs.values():
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"created: {dir_path}")

    return output_dirs

def filter_available_skills(author_skills, sample_task):
    # filter out unavailable skills
    available_skills = set()
    for skills in author_skills.values():
        available_skills.update(skills)

    # only keep skills that are in the sample task
    filtered_task = sample_task & available_skills
    missing_skills = sample_task - available_skills
    
    if missing_skills:
        print(f" no skills available: {list(missing_skills)[:5]}{'...' if len(missing_skills) > 5 else ''}")

    return filtered_task

def run_algorithm(algorithm_func, algorithm_name, G, author_skills, filtered_task, output_dirs):
    # short test
    print(f"\n{'=' * 40}")
    print(f"Testing {algorithm_name} algorithm")
    print(f"{'=' * 40}")
    
    try:
        # record start time
        start_time = time.time()

        # run algorithm
        team, cost, connected = algorithm_func(G, author_skills, filtered_task)
        
        # compute execution time
        execution_time = time.time() - start_time

        # construct result
        result = {
            "algorithm": algorithm_name,
            "team": list(team) if team else [],
            "team_size": len(team) if team else 0,
            "cost": cost,
            "connected": connected,
            "execution_time": execution_time,
            "success": True
        }

        # visualize and save
        if team:
            visualize_team(G, team, author_skills, filtered_task, algorithm_name, output_dirs)
        else:
            print(f" {algorithm_name} see no team members to visualize.")

        return result
        
    except Exception as e:
        execution_time = time.time() - start_time if 'start_time' in locals() else 0
        print(f" {algorithm_name} algorithm test failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "algorithm": algorithm_name,
            "error": str(e),
            "execution_time": execution_time,
            "success": False
        }

def print_result_summary(result):
    # print result summary
    algorithm_name = result.get("algorithm", "Unknown")
    execution_time = result.get("execution_time", 0)
    
    print(f"\n{algorithm_name} result:")
    print(f"   Execution time: {execution_time:.3f}s")

    if not result.get("success", False):
        print(f"   error: {result.get('error', 'Unknown error')}")
    else:
        print(f"   Team size: {result['team_size']}")
        print(f"   Communication cost: {result['cost']:.4f}")
        print(f"   Connectivity: {'Yes' if result['connected'] else 'No'}")
        if result['team']:
            team_preview = result['team'][:3]
            more = "..." if len(result['team']) > 3 else ""
            print(f"   Team members: {team_preview}{more}")

def run_algorithm_test(algorithms=None):
    print("=" * 60)
    print("Testing team formation algorithms")
    print("=" * 60)

    # ensure output directories exist
    output_dirs = ensure_directories()
    
    # sample task skills
    sample_task = {
        "object detection", "image classification", "semantic segmentation", "instance segmentation",
        "image generation", "image super resolution", "object recognition", "pose estimation",
        "face recognition", "facial expression recognition", "visual tracking", "depth estimation",
        "optical flow estimation", "novel view synthesis", "image restoration", "image enhancement",
        "denoising", "style transfer", "image captioning", "visual question answering",
        "image to image translation"
    }

    print(f" num of skills: {len(sample_task)}")

    # load data
    print("\n Loading data...")
    try:
        G, author_skills = load_data()
        print(f" Graph data: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        print(f" Author skills data: {len(author_skills)} authors")

        # filter available skills
        filtered_task = filter_available_skills(author_skills, sample_task)
        print(f" Number of covered skills: {len(filtered_task)}")

        if not filtered_task:
            print(" No covered skills available for testing")
            return
            
    except Exception as e:
        print(f" Failed to load data: {e}")
        return

    # available algorithms mapping
    available_algorithms = {
        "CoverSteiner": cover_steiner,
        "EnhanceSteiner": enhanced_steiner,
        "GraphAwareCoverSteiner": graph_aware_cover_steiner,
        "ImprovedEnhanceSteiner": improved_enhance_steiner
    }

    # determine which algorithms to test
    if algorithms is None:
        test_algorithms = available_algorithms
    else:
        test_algorithms = {}
        for alg in algorithms:
            # name mapping
            if alg in ["cover_steiner", "CoverSteiner"]:
                test_algorithms["CoverSteiner"] = available_algorithms["CoverSteiner"]
            elif alg in ["enhance_steiner", "EnhanceSteiner"]:
                test_algorithms["EnhanceSteiner"] = available_algorithms["EnhanceSteiner"]
            elif alg in ["graph_aware_cover_steiner", "GraphAwareCoverSteiner"]:
                test_algorithms["GraphAwareCoverSteiner"] = available_algorithms["GraphAwareCoverSteiner"]
            elif alg in ["improved_enhance_steiner", "ImprovedEnhanceSteiner"]:
                test_algorithms["ImprovedEnhanceSteiner"] = available_algorithms["ImprovedEnhanceSteiner"]
            else:
                print(f" unknown algorithm: {alg}")

    if not test_algorithms:
        print(" No available algorithms found for testing")
        return
    
    # run each algorithm and collect results
    results = {}
    for algorithm_name, algorithm_func in test_algorithms.items():
        result = run_algorithm(algorithm_func, algorithm_name, G, author_skills, filtered_task, output_dirs)
        results[algorithm_name] = result
        print_result_summary(result)

    # output summary (including time comparison)
    print(f"\n{'=' * 60}")
    print("Testing Results Summary")
    print(f"{'=' * 60}")

    # Sort results by execution time
    sorted_results = sorted(results.items(), key=lambda x: x[1].get("execution_time", float('inf')))
    
    for algorithm_name, result in sorted_results:
        print_result_summary(result)

    # display execution time comparison
    if len(results) > 1:
        print(f"\n execution time comparison:")
        for algorithm_name, result in sorted_results:
            if result.get("success", False):
                exec_time = result.get("execution_time", 0)
                print(f"  {algorithm_name}: {exec_time:.3f}s")


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Team Formation Algorithm Testing Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  python test_algorithms.py                           # Test all algorithms
  python test_algorithms.py cover_steiner             # Test only CoverSteiner
  python test_algorithms.py enhance_steiner           # Test only EnhancedSteiner
  python test_algorithms.py cover_steiner enhance_steiner  # Test both algorithms

Available algorithms:
  cover_steiner    - CoverSteiner algorithm
  enhance_steiner  - EnhancedSteiner algorithm
  improved_enhance_steiner - ImprovedEnhanceSteiner algorithm
        """
    )
    
    parser.add_argument(
        'algorithms',
        nargs='*',
        choices=['cover_steiner', 'enhance_steiner', 'graph_aware_cover_steiner', 'improved_enhance_steiner'],
        help='algorithm names to test (multiple choices allowed). If not specified, all algorithms will be tested.'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # if no specific algorithms are provided, test all available algorithms
    algorithms_to_test = args.algorithms if args.algorithms else None
    
    if algorithms_to_test:
        print(f" chosen algorithms: {', '.join(algorithms_to_test)}")
    else:
        print(" Testing all available algorithms")

    run_algorithm_test(algorithms_to_test)