"""
Ant Count Optimization Experiment
Tests different ant colony sizes [10, 20, 30, 40, 50, 75, 100] and records:
- Work done at milestone iterations
- Iterations needed to reach first viable no-daylight route
- Total runtime
- Identifies optimal ant count
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import csv
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# --- configuration ---
import os
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, 'main.py')

ANT_COUNTS = [5, 10, 25,  50, 75]
NUM_RUNS_PER_ANT_COUNT = 3  # Multiple runs for statistical significance
CHECKPOINT_ITERATIONS = [100, 500, 1000]  # Milestone iterations to record metrics
NUM_ITERATIONS = 1000
PARENT_EXPERIMENTS_DIR = os.path.expanduser('~/Desktop/Dissertation Travelling Santa Problem')
EXPERIMENT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'ant_optimization3')

# --- utility: import and modify main algorithm ---
def run_tsp_with_ant_count(ant_count: int, experiment_dir: str) -> Dict[str, Any]:
    """
    Run the main TSP algorithm with specified ant count.
    Returns dictionary with metrics.
    """
    import importlib.util

    # Read the main script
    with open(MAIN_SCRIPT, 'r') as f:
        main_code = f.read()
    
    # Modify parameters
    main_code = main_code.replace(
        "MAIN_OUTPUT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'main_run')",
        f"MAIN_OUTPUT_DIR = r'{experiment_dir}'"
    )
    main_code = main_code.replace(
        "NUM_ANTS = 50",
        f"NUM_ANTS = {ant_count}"
    )
    main_code = main_code.replace(
        "NUM_ITERATIONS = 6000",
        f"NUM_ITERATIONS = {NUM_ITERATIONS}"
    )
    
    # Execute
    start_time = time.time()
    exec_globals = {'__name__': '__main__'}
    exec(main_code, exec_globals)
    end_time = time.time()
    
    runtime = end_time - start_time
    
    # Extract metrics
    metrics_csv = os.path.join(experiment_dir, 'iteration_metrics.csv')
    
    results = {
        'ant_count': ant_count,
        'runtime_seconds': runtime,
        'iterations_to_viable': None,
        'work_at_checkpoints': {},
        'effective_cost_at_checkpoints': {},
        'final_tour_length': None,
        'final_effective_cost': None
    }
    
    if os.path.exists(metrics_csv):
        with open(metrics_csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Find first iteration with no penalty
            for row in rows:
                iteration = int(row['Iteration'])
                has_penalty = row['Has Daylight Penalty'] == 'Yes'
                if not has_penalty and results['iterations_to_viable'] is None:
                    results['iterations_to_viable'] = iteration
            
            # Extract work at checkpoints
            for row in rows:
                iteration = int(row['Iteration'])
                if iteration in CHECKPOINT_ITERATIONS:
                    results['work_at_checkpoints'][iteration] = float(row['Best Total Work (J)'])
                    results['effective_cost_at_checkpoints'][iteration] = float(row['Best Effective Cost (J)'])
            
            # Final metrics
            if rows:
                last_row = rows[-1]
                results['final_tour_length'] = float(last_row['Best Tour Length (km)'])
                results['final_effective_cost'] = float(last_row['Best Effective Cost (J)'])
    
    return results

# --- plotting functions ---
def plot_work_comparison(all_results: Dict[int, List[Dict[str, Any]]], filename: str) -> None:
    """Plot work done at checkpoints for different ant counts."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for ant_count in sorted(ANT_COUNTS):
        runs = all_results[ant_count]
        avg_work = {}
        
        for checkpoint in CHECKPOINT_ITERATIONS:
            works = []
            for run in runs:
                if checkpoint in run['work_at_checkpoints']:
                    works.append(run['work_at_checkpoints'][checkpoint])
            if works:
                avg_work[checkpoint] = np.mean(works)
        
        if avg_work:
            ax.plot(sorted(avg_work.keys()), [avg_work[c] for c in sorted(avg_work.keys())],
                   marker='o', label=f'{ant_count} ants')
    
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Work (Joules)')
    ax.set_title('Work Done at Checkpoints vs Ant Count')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.set_yscale('log')
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_iterations_to_viable(ant_counts: List[int], iterations_to_viable: List[float], filename: str) -> None:
    """Plot iterations needed to reach viable solution vs ant count."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ant_counts, iterations_to_viable, marker='o', linewidth=2, markersize=8)
    ax.set_xlabel('Number of Ants')
    ax.set_ylabel('Iterations to First Viable Route')
    ax.set_title('Convergence Speed vs Ant Count')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_runtime_vs_ants(ant_counts: List[int], runtimes: List[float], filename: str) -> None:
    """Plot total runtime vs ant count."""
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ant_counts, runtimes, marker='s', linewidth=2, markersize=8, color='red')
    ax.set_xlabel('Number of Ants')
    ax.set_ylabel('Total Runtime (seconds)')
    ax.set_title('Computational Cost vs Ant Count')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_efficiency_metric(ant_counts: List[int], viables: List[float], runtimes: List[float], filename: str) -> None:
    """Plot efficiency metric: viable iterations / (iterations per second)."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Efficiency = iterations to viable per second of runtime (lower is better)
    efficiencies = []
    for viable, runtime in zip(viables, runtimes):
        if viable and runtime > 0:
            # Iterations per second
            iter_per_sec = NUM_ITERATIONS / runtime
            # Quality per second (inverse of iterations needed)
            efficiency = iter_per_sec / viable if viable > 0 else 0
            efficiencies.append(efficiency)
        else:
            efficiencies.append(0)
    
    ax.plot(ant_counts, efficiencies, marker='D', linewidth=2, markersize=8, color='green')
    ax.set_xlabel('Number of Ants')
    ax.set_ylabel('Efficiency (Iter/Sec / Iter to Viable)')
    ax.set_title('Algorithmic Efficiency vs Ant Count')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# --- main execution ---
def main() -> None:
    os.makedirs(EXPERIMENT_DIR, exist_ok=True)
    
    logging.info(f"Starting ant count optimization experiment")
    logging.info(f"Testing ant counts: {ANT_COUNTS}")
    logging.info(f"Runs per ant count: {NUM_RUNS_PER_ANT_COUNT}")
    
    all_results: Dict[int, List[Dict[str, Any]]] = {ant_count: [] for ant_count in ANT_COUNTS}
    summary_data: List[Dict[str, Any]] = []
    
    # Run experiments
    total_runs = len(ANT_COUNTS) * NUM_RUNS_PER_ANT_COUNT
    run_count = 0
    
    for ant_count in ANT_COUNTS:
        logging.info(f"\nTesting with {ant_count} ants...")
        
        for run_num in range(1, NUM_RUNS_PER_ANT_COUNT + 1):
            run_count += 1
            logging.info(f"  Run {run_num}/{NUM_RUNS_PER_ANT_COUNT} (overall {run_count}/{total_runs})")
            
            exp_dir = os.path.join(EXPERIMENT_DIR, f'ants_{ant_count}_run_{run_num}')
            
            try:
                results = run_tsp_with_ant_count(ant_count, exp_dir)
                all_results[ant_count].append(results)
                summary_data.append(results)
                
                logging.info(f"    Runtime: {results['runtime_seconds']:.1f}s")
                if results['iterations_to_viable']:
                    logging.info(f"    Iterations to viable: {results['iterations_to_viable']}")
                else:
                    logging.info(f"    No viable route found within {NUM_ITERATIONS} iterations")
                
            except Exception as e:
                logging.error(f"  Run failed: {e}")
    
    # Generate summary statistics
    summary_csv = os.path.join(EXPERIMENT_DIR, 'ant_optimization_summary.csv')
    with open(summary_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Ant Count', 'Avg Iterations to Viable', 'Std Iterations', 
            'Avg Runtime (s)', 'Std Runtime', 'Avg Final Cost',
            'Best Final Cost', 'Worst Final Cost'
        ])
        writer.writeheader()
        
        for ant_count in ANT_COUNTS:
            runs = all_results[ant_count]
            if not runs:
                continue
            
            iterations_to_viable = [r['iterations_to_viable'] for r in runs if r['iterations_to_viable']]
            runtimes = [r['runtime_seconds'] for r in runs]
            final_costs = [r['final_effective_cost'] for r in runs if r['final_effective_cost']]
            
            writer.writerow({
                'Ant Count': ant_count,
                'Avg Iterations to Viable': round(np.mean(iterations_to_viable), 2) if iterations_to_viable else 'N/A',
                'Std Iterations': round(np.std(iterations_to_viable), 2) if iterations_to_viable else 'N/A',
                'Avg Runtime (s)': round(np.mean(runtimes), 2),
                'Std Runtime': round(np.std(runtimes), 2),
                'Avg Final Cost': round(np.mean(final_costs), 2) if final_costs else 'N/A',
                'Best Final Cost': round(np.min(final_costs), 2) if final_costs else 'N/A',
                'Worst Final Cost': round(np.max(final_costs), 2) if final_costs else 'N/A'
            })
    
    # Export detailed results
    detailed_csv = os.path.join(EXPERIMENT_DIR, 'all_ant_runs.csv')
    with open(detailed_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'Ant Count', 'Run', 'Runtime (s)', 'Iterations to Viable',
            'Final Tour Length (km)', 'Final Effective Cost (J)'
        ])
        writer.writeheader()
        
        for data in summary_data:
            writer.writerow({
                'Ant Count': data['ant_count'],
                'Run': '',  # Would need to track run number separately
                'Runtime (s)': round(data['runtime_seconds'], 2),
                'Iterations to Viable': data['iterations_to_viable'] if data['iterations_to_viable'] else 'N/A',
                'Final Tour Length (km)': round(data['final_tour_length'], 2) if data['final_tour_length'] else 'N/A',
                'Final Effective Cost (J)': round(data['final_effective_cost'], 2) if data['final_effective_cost'] else 'N/A'
            })
    
    # Generate plots
    ant_counts_with_data = [ant_count for ant_count in ANT_COUNTS if all_results[ant_count]]
    
    if ant_counts_with_data:
        # Plot 1: Work at checkpoints
        plot_file_1 = os.path.join(EXPERIMENT_DIR, 'work_at_checkpoints.png')
        plot_work_comparison(all_results, plot_file_1)
        
        # Plot 2: Iterations to viable
        iterations_to_viable = []
        for ant_count in ant_counts_with_data:
            runs = all_results[ant_count]
            viable_iters = [r['iterations_to_viable'] for r in runs if r['iterations_to_viable']]
            if viable_iters:
                iterations_to_viable.append(np.mean(viable_iters))
            else:
                iterations_to_viable.append(NUM_ITERATIONS)  # Didn't converge
        
        plot_file_2 = os.path.join(EXPERIMENT_DIR, 'iterations_to_viable.png')
        plot_iterations_to_viable(ant_counts_with_data, iterations_to_viable, plot_file_2)
        
        # Plot 3: Runtime
        runtimes = []
        for ant_count in ant_counts_with_data:
            runs = all_results[ant_count]
            avg_runtime = np.mean([r['runtime_seconds'] for r in runs])
            runtimes.append(avg_runtime)
        
        plot_file_3 = os.path.join(EXPERIMENT_DIR, 'runtime_vs_ants.png')
        plot_runtime_vs_ants(ant_counts_with_data, runtimes, plot_file_3)
        
        # Plot 4: Efficiency
        plot_file_4 = os.path.join(EXPERIMENT_DIR, 'efficiency_metric.png')
        plot_efficiency_metric(ant_counts_with_data, iterations_to_viable, runtimes, plot_file_4)
        
        # Determine optimal ant count
        efficiency_scores = []
        for ant_count, viable in zip(ant_counts_with_data, iterations_to_viable):
            runs = all_results[ant_count]
            avg_runtime = np.mean([r['runtime_seconds'] for r in runs])
            # Score: lower iterations to viable + lower runtime (normalized)
            score = viable / NUM_ITERATIONS + avg_runtime / (NUM_ITERATIONS / 100)
            efficiency_scores.append((ant_count, score))
        
        optimal_ant_count, _ = min(efficiency_scores, key=lambda x: x[1])
        
        # Write recommendation
        recommendation_file = os.path.join(EXPERIMENT_DIR, 'RECOMMENDATION.txt')
        with open(recommendation_file, 'w') as f:
            f.write("ANT COUNT OPTIMIZATION RESULTS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Optimal ant count: {optimal_ant_count} ants\n\n")
            f.write("Efficiency scores (lower is better):\n")
            for ant_count, score in sorted(efficiency_scores):
                f.write(f"  {ant_count} ants: {score:.4f}\n")
    
    logging.info(f"\nExperiment complete! Results saved to {EXPERIMENT_DIR}")
    logging.info(f"Summary CSV: {summary_csv}")
    logging.info(f"Detailed CSV: {detailed_csv}")

if __name__ == '__main__':
    main()
