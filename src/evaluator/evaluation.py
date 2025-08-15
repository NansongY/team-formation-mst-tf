import json
import time
import networkx as nx
import matplotlib.pyplot as plt
import os
import sys
from collections import defaultdict

# add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from algorithm.cover_steiner import cover_steiner
from algorithm.graph_aware_cover_steiner import graph_aware_cover_steiner
from algorithm.improved_enhance_steiner import improved_enhance_steiner
from data_processing.config import DATA_PATHS

def load_data():
    # load graph and author skills from predefined paths
    print(" Loading data...")
    
    # Load graph
    G = nx.read_gexf(DATA_PATHS["graph_gexf"], node_type=str)
    
    # Normalize node names
    node_mapping = {node: node.encode('utf-8').decode('utf-8') for node in G.nodes()}
    G = nx.relabel_nodes(G, node_mapping)

    # Load author skills
    with open(DATA_PATHS["author_skills"], encoding='utf-8') as f:
        author_skills_raw = json.load(f)
        author_skills = {
            author.encode('utf-8').decode('utf-8'): set(skills) if isinstance(skills, list) else skills
            for author, skills in author_skills_raw.items()
        }

    # Load generated tasks
    tasks_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                             "data", "evaluation", "generated_tasks.json")
    with open(tasks_file, encoding='utf-8') as f:
        tasks = json.load(f)

    print(f" Loading graph data: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    print(f" Loading author data: {len(author_skills)} authors")
    print(f" Loading task data: {len(tasks)} tasks")

    return G, author_skills, tasks

def evaluate_task_with_algorithm(G, author_skills, task, algorithm_func, algorithm_name):
    """Evaluate the performance of a single task using the specified algorithm"""
    skill_set = set(task["skills"])
    t = task["t"]
    s = task["s"]
    
    try:
        start_time = time.time()
        team, cost, connected = algorithm_func(G, author_skills, skill_set)
        execution_time = time.time() - start_time
        
        team_size = len(team) if team else 0

        # When team size is 1, set communication cost to 0
        if team_size == 1:
            cost = 0
        elif team_size == 0:
            cost = float('inf')

        # Calculate skill coverage
        if team:
            covered_skills_set = set.union(*[author_skills.get(a, set()) for a in team])
            covered_skills = len(skill_set & covered_skills_set)
        else:
            covered_skills = 0
        
        result = {
            "algorithm": algorithm_name,
            "t": t,
            "s": s,
            "team_size": team_size,
            "required_skills": len(skill_set),
            "covered_skills": covered_skills,
            "communication_cost": float('inf') if cost is None else cost,
            "is_connected": connected,
            "execution_time": execution_time,
            "success": covered_skills == len(skill_set) and team_size > 0
        }
        
        return result
        
    except Exception as e:
        print(f" {algorithm_name} evaluation failed: {e}")
        return {
            "algorithm": algorithm_name,
            "t": t,
            "s": s,
            "team_size": 0,
            "required_skills": len(skill_set),
            "covered_skills": 0,
            "communication_cost": float('inf'),
            "is_connected": False,
            "execution_time": 0,
            "success": False,
            "error": str(e)
        }

def calculate_statistics(results, algorithm_name):
    # Calculate statistics for a specific algorithm from the results
    # Group by t value
    stats = defaultdict(list)
    for r in results:
        if r["algorithm"] == algorithm_name:
            stats[r["t"]].append(r)
    
    summary = {}
    for t in sorted(stats.keys()):
        t_results = stats[t]

        # Calculate average team size
        avg_team_size = sum(r["team_size"] for r in t_results) / len(t_results)

        # Calculate average communication cost (only consider valid values)
        valid_costs = [r["communication_cost"] for r in t_results
                      if r["communication_cost"] != float('inf') and r["team_size"] > 0]
        avg_cost = sum(valid_costs) / len(valid_costs) if valid_costs else float('inf')

        # Calculate success rate
        success_rate = sum(1 for r in t_results if r["success"]) / len(t_results)

        # Calculate average execution time
        avg_execution_time = sum(r["execution_time"] for r in t_results) / len(t_results)
        
        summary[str(t)] = {
            "average_team_size": round(avg_team_size, 2),
            "average_communication_cost": round(float(avg_cost), 2) if avg_cost != float('inf') else "inf",
            "success_rate": round(success_rate * 100, 1),
            "average_execution_time": round(avg_execution_time, 3),
            "valid_cost_samples": f"{len(valid_costs)}/{len(t_results)}",
            "total_tasks": len(t_results)
        }
    
    return summary

def generate_cost_plots(results, output_dir):
    # Generate cost comparison plots for different algorithms
    print(" Generating visualization plots...")
    
    # Get all algorithms
    algorithms = list(set(r["algorithm"] for r in results))
    
    # Group data by algorithm
    algorithm_data = defaultdict(lambda: defaultdict(list))
    
    for result in results:
        if result["communication_cost"] != float('inf') and result["success"]:
            t = result["t"]
            cost = result["communication_cost"]
            algorithm = result["algorithm"]
            algorithm_data[algorithm][t].append(cost)

    # Prepare plotting data
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    markers = ['o', 's', '^', 'D', 'v']
    
    # figure 1: Average communication cost
    for i, algorithm in enumerate(algorithms):
        t_values = []
        avg_costs = []
        
        for t in sorted(algorithm_data[algorithm].keys()):
            costs = algorithm_data[algorithm][t]
            if costs:
                t_values.append(t)
                avg_costs.append(sum(costs) / len(costs))
        
        if t_values and avg_costs:
            ax1.plot(t_values, avg_costs, 
                    marker=markers[i % len(markers)], 
                    color=colors[i % len(colors)],
                    linewidth=2, markersize=8,
                    label=algorithm)
    
    ax1.set_xlabel('Skills (t)', fontsize=12)
    ax1.set_ylabel('Average Communication Cost', fontsize=12)
    ax1.set_title('Comparison of Average Communication Cost for Different Algorithms', fontsize=14, fontweight='bold')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')  # Use logarithmic scale

    # figure 2: Average team size
    for i, algorithm in enumerate(algorithms):
        algorithm_results = [r for r in results if r["algorithm"] == algorithm]
        team_size_data = defaultdict(list)
        
        for result in algorithm_results:
            if result["success"]:
                team_size_data[result["t"]].append(result["team_size"])
        
        t_values = []
        avg_team_sizes = []
        
        for t in sorted(team_size_data.keys()):
            sizes = team_size_data[t]
            if sizes:
                t_values.append(t)
                avg_team_sizes.append(sum(sizes) / len(sizes))
        
        if t_values and avg_team_sizes:
            ax2.plot(t_values, avg_team_sizes,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    linewidth=2, markersize=8,
                    label=algorithm)

    ax2.set_xlabel('Skills (t)', fontsize=12)
    ax2.set_ylabel('Average Team Size', fontsize=12)
    ax2.set_title('Comparison of Average Team Size for Different Algorithms', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()

    # save plot
    plot_path = os.path.join(output_dir, "algorithm_comparison.png")
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f" Saving comparison plot: {plot_path}")

    # Generate success rate plot
    plt.figure(figsize=(10, 6))
    
    for i, algorithm in enumerate(algorithms):
        algorithm_results = [r for r in results if r["algorithm"] == algorithm]
        success_data = defaultdict(list)
        
        for result in algorithm_results:
            success_data[result["t"]].append(1 if result["success"] else 0)
        
        t_values = []
        success_rates = []
        
        for t in sorted(success_data.keys()):
            successes = success_data[t]
            if successes:
                t_values.append(t)
                success_rates.append(sum(successes) / len(successes) * 100)
        
        if t_values and success_rates:
            plt.plot(t_values, success_rates,
                    marker=markers[i % len(markers)],
                    color=colors[i % len(colors)],
                    linewidth=2, markersize=8,
                    label=algorithm)

    plt.xlabel('Skills (t)', fontsize=12)
    plt.ylabel('Success Rate (%)', fontsize=12)
    plt.title('Comparison of Success Rate for Different Algorithms', fontsize=14, fontweight='bold')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 105)
    
    success_plot_path = os.path.join(output_dir, "success_rate_comparison.png")
    plt.savefig(success_plot_path, dpi=300, bbox_inches='tight')
    print(f" Saving success rate plot: {success_plot_path}")

    plt.close('all')

def main():
    print(" Starting multi-algorithm evaluation")
    print("=" * 60)

    # Load data
    G, author_skills, tasks = load_data()

    # Define algorithms to test
    algorithms = {
        "CoverSteiner": cover_steiner,
        "GraphAwareCoverSteiner": graph_aware_cover_steiner,
        "ImprovedEnhanceSteiner": improved_enhance_steiner
    }

    # Ensure output directory exists
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                             "data", "visualized")
    os.makedirs(output_dir, exist_ok=True)
    
    results = []
    total_evaluations = len(tasks) * len(algorithms)
    current_evaluation = 0

    print(f" Starting evaluation of {len(tasks)} tasks × {len(algorithms)} algorithms = {total_evaluations} evaluations")

    # Evaluate each algorithm and each task
    for algorithm_name, algorithm_func in algorithms.items():
        print(f"\n Testing {algorithm_name} algorithm...")
        
        for i, task in enumerate(tasks, 1):
            current_evaluation += 1
            
            try:
                result = evaluate_task_with_algorithm(G, author_skills, task, algorithm_func, algorithm_name)
                results.append(result)
                
                # save results to file
                if current_evaluation % 20 == 0:
                    progress = (current_evaluation / total_evaluations) * 100
                    print(f"  Progress: {current_evaluation}/{total_evaluations} ({progress:.1f}%)")

            except Exception as e:
                print(f" Evaluation failed (Task {i}, Algorithm {algorithm_name}): {e}")
                continue

    print(f"\n Evaluation completed, collected {len(results)} results")

    # Calculate statistics for each algorithm
    print("\n Calculating statistics...")
    all_summaries = {}
    
    for algorithm_name in algorithms.keys():
        print(f"\n{algorithm_name} algorithm results:")
        summary = calculate_statistics(results, algorithm_name)
        all_summaries[algorithm_name] = summary
        
        for t in sorted([int(k) for k in summary.keys()]):
            t_str = str(t)
            s = summary[t_str]
            print(f"  t={t}:")
            print(f"    Average Team Size: {s['average_team_size']}")
            print(f"    Average Communication Cost: {s['average_communication_cost']}")
            print(f"    Success Rate: {s['success_rate']}%")
            print(f"    Average Execution Time: {s['average_execution_time']}s")
            print(f"    Valid Samples: {s['valid_cost_samples']}")

    # Generate visualizations
    generate_cost_plots(results, output_dir)

    # Save full results
    full_results = {
        "evaluation_summary": {
            "total_tasks": len(tasks),
            "algorithms_tested": list(algorithms.keys()),
            "total_evaluations": len(results)
        },
        "algorithm_summaries": all_summaries,
        "detailed_results": results
    }
    
    results_file = os.path.join(os.path.dirname(output_dir), "processed", "evaluation_results.json")
    os.makedirs(os.path.dirname(results_file), exist_ok=True)
    
    with open(results_file, "w", encoding='utf-8') as f:
        json.dump(full_results, f, indent=2, ensure_ascii=False)

    print(f"\n Saving detailed results: {results_file}")
    print("\n Multi-algorithm evaluation completed!")

if __name__ == "__main__":
    main()