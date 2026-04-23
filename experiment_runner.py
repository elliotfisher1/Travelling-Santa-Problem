"""
Multi-Run Experiment Wrapper
Runs the full TSP algorithm multiple times (default 30 runs), records statistics,
and generates boxplot and summary table.
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import csv
import subprocess
import sys
import time
from datetime import datetime
from typing import List, Dict, Any

# ==============================================================================
# Configuration
# ==============================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

NUM_RUNS = 15  # Scaled down from 30
NUM_ITERATIONS = 1000  # Half of default 6000
NUM_ANTS = 15  # Half of default 50
PARENT_EXPERIMENTS_DIR = os.path.expanduser('~/Desktop/Dissertation Travelling Santa Problem')
EXPERIMENT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'multi_run_experiment')

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================
def run_single_experiment(run_number: int, run_dir: str) -> Dict[str, Any]:
    """
    Run a single iteration of the full TSP algorithm.
    Returns dictionary with final metrics.
    """
    logging.info(f"Starting run {run_number}/{NUM_RUNS}")

    # Create temporary output directory for this run
    os.makedirs(run_dir, exist_ok=True)

    # Import main.py dynamically to run it with modified output directory
    import importlib.util
    spec = importlib.util.spec_from_file_location("main_module", "/Users/elliotfisher/Travelling-Santa-Problem-1/main.py")
    main_module = importlib.util.module_from_spec(spec)

    # Override output directory
    start_time = time.time()
    
    # We'll read the main.py and execute with modified output dir
    with open("/Users/elliotfisher/Travelling-Santa-Problem-1/main.py", 'r') as f:
        main_code = f.read()
    
    # Replace the main output directory (match actual definition in main.py)
    main_code = main_code.replace(
        "MAIN_OUTPUT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'main_run')",
        f"MAIN_OUTPUT_DIR = r'{run_dir}'"
    )
    
    # Scale down the experiment parameters
    main_code = main_code.replace("NUM_ITERATIONS = 6000", f"NUM_ITERATIONS = {NUM_ITERATIONS}")
    main_code = main_code.replace("NUM_ANTS = 50", f"NUM_ANTS = {NUM_ANTS}")
    
    # Execute the modified code
    exec_globals = {'__name__': '__main__'}
    exec(main_code, exec_globals)
    
    end_time = time.time()
    runtime = end_time - start_time

    # Extract final metrics from iteration_metrics.csv
    metrics_csv = os.path.join(run_dir, 'iteration_metrics.csv')
    final_metrics = {
        'run': run_number,
        'runtime_seconds': runtime,
        'best_tour_length': None,
        'best_travel_time': None,
        'best_waiting_time': None,
        'best_work': None,
        'best_effective_cost': None,
        'has_penalty': None
    }

    if os.path.exists(metrics_csv):
        try:
            with open(metrics_csv, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    last_row = rows[-1]
                    final_metrics['best_tour_length'] = float(last_row['Best Tour Length (km)'])
                    final_metrics['best_travel_time'] = float(last_row['Best Travel Time (h)'])
                    final_metrics['best_waiting_time'] = float(last_row['Best Waiting Time (h)'])
                    final_metrics['best_work'] = float(last_row['Best Total Work (J)'])
                    final_metrics['best_effective_cost'] = float(last_row['Best Effective Cost (J)'])
                    final_metrics['has_penalty'] = last_row['Has Daylight Penalty']
        except Exception as e:
            logging.warning(f"Could not parse metrics CSV for run {run_number}: {e}")
            return None

    if final_metrics['best_tour_length'] is not None:
        logging.info(f"Run {run_number} complete. Tour length: {final_metrics['best_tour_length']:.2f} km, Runtime: {runtime:.1f}s")
    else:
        logging.warning(f"Run {run_number} produced no valid metrics")
    return final_metrics

def plot_boxplot(data: List[float], metric_name: str, filename: str) -> None:
    """Create boxplot for a metric across all runs."""
    fig, ax = plt.subplots(figsize=(10, 6))
    bp = ax.boxplot([data], labels=[metric_name])
    ax.set_ylabel('Value')
    ax.set_title(f'Distribution of {metric_name} Across {NUM_RUNS} Runs')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def plot_comparison_boxplots(all_metrics: List[Dict[str, Any]], filename: str) -> None:
    """Create multiple boxplots for key metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    tour_lengths = [m['best_tour_length'] for m in all_metrics if m['best_tour_length'] is not None]
    travel_times = [m['best_travel_time'] for m in all_metrics if m['best_travel_time'] is not None]
    works = [m['best_work'] for m in all_metrics if m['best_work'] is not None]
    eff_costs = [m['best_effective_cost'] for m in all_metrics if m['best_effective_cost'] is not None]

    axes[0, 0].boxplot([tour_lengths])
    axes[0, 0].set_ylabel('Distance (km)')
    axes[0, 0].set_title('Tour Length Distribution')
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].boxplot([travel_times])
    axes[0, 1].set_ylabel('Time (hours)')
    axes[0, 1].set_title('Travel Time Distribution')
    axes[0, 1].grid(True, alpha=0.3)

    axes[1, 0].boxplot([works])
    axes[1, 0].set_ylabel('Work (Joules)')
    axes[1, 0].set_title('Total Work Distribution')
    axes[1, 0].set_yscale('log')
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].boxplot([eff_costs])
    axes[1, 1].set_ylabel('Effective Cost (Joules)')
    axes[1, 1].set_title('Effective Cost Distribution')
    axes[1, 1].set_yscale('log')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

def generate_summary_table(all_metrics: List[Dict[str, Any]], filename: str) -> None:
    """Generate summary statistics table."""
    if not all_metrics:
        logging.warning("No valid metrics to generate summary table")
        return
    
    tour_lengths = [m['best_tour_length'] for m in all_metrics if m['best_tour_length'] is not None]
    travel_times = [m['best_travel_time'] for m in all_metrics if m['best_travel_time'] is not None]
    works = [m['best_work'] for m in all_metrics if m['best_work'] is not None]
    eff_costs = [m['best_effective_cost'] for m in all_metrics if m['best_effective_cost'] is not None]
    runtimes = [m['runtime_seconds'] for m in all_metrics]
    penalties = [m['has_penalty'] for m in all_metrics if m['has_penalty'] is not None]
    
    if not tour_lengths:
        logging.warning("No valid tour lengths found")
        return

    summary = {
        'Metric': ['Tour Length (km)', 'Travel Time (h)', 'Total Work (J)', 'Effective Cost (J)', 'Runtime (s)'],
        'Mean': [
            np.mean(tour_lengths),
            np.mean(travel_times),
            np.mean(works),
            np.mean(eff_costs),
            np.mean(runtimes)
        ],
        'Std Dev': [
            np.std(tour_lengths),
            np.std(travel_times),
            np.std(works),
            np.std(eff_costs),
            np.std(runtimes)
        ],
        'Best': [
            np.min(tour_lengths),
            np.min(travel_times),
            np.min(works),
            np.min(eff_costs),
            np.min(runtimes)
        ],
        'Worst': [
            np.max(tour_lengths),
            np.max(travel_times),
            np.max(works),
            np.max(eff_costs),
            np.max(runtimes)
        ]
    }

    with open(filename, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Metric', 'Mean', 'Std Dev', 'Best', 'Worst'])
        writer.writeheader()
        for i, metric in enumerate(summary['Metric']):
            writer.writerow({
                'Metric': metric,
                'Mean': round(summary['Mean'][i], 2),
                'Std Dev': round(summary['Std Dev'][i], 2),
                'Best': round(summary['Best'][i], 2),
                'Worst': round(summary['Worst'][i], 2)
            })

    # Also write as text for readability
    txt_filename = filename.replace('.csv', '.txt')
    with open(txt_filename, 'w') as f:
        f.write(f"Multi-Run Experiment Summary ({NUM_RUNS} runs)\n")
        f.write("=" * 80 + "\n\n")
        for i, metric in enumerate(summary['Metric']):
            f.write(f"{metric}:\n")
            f.write(f"  Mean:    {summary['Mean'][i]:.2f}\n")
            f.write(f"  Std Dev: {summary['Std Dev'][i]:.2f}\n")
            f.write(f"  Best:    {summary['Best'][i]:.2f}\n")
            f.write(f"  Worst:   {summary['Worst'][i]:.2f}\n\n")

        # Penalty statistics
        penalty_count = sum(1 for p in penalties if p == 'Yes')
        f.write(f"Daylight Penalty Statistics:\n")
        f.write(f"  Runs with penalty: {penalty_count}/{len(penalties)}\n")
        f.write(f"  Success rate (no penalty): {(len(penalties)-penalty_count)/len(penalties)*100:.1f}%\n")

    logging.info(f"Summary table saved to {txt_filename}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main() -> None:
    os.makedirs(EXPERIMENT_DIR, exist_ok=True)

    logging.info(f"Starting multi-run experiment with {NUM_RUNS} runs")
    logging.info(f"Results will be saved to {EXPERIMENT_DIR}")

    all_metrics: List[Dict[str, Any]] = []

    # Run experiments
    for run_num in range(1, NUM_RUNS + 1):
        run_dir = os.path.join(EXPERIMENT_DIR, f'run_{run_num:02d}')
        try:
            metrics = run_single_experiment(run_num, run_dir)
            if metrics is not None:  # Only add successful runs
                all_metrics.append(metrics)
        except Exception as e:
            logging.error(f"Run {run_num} failed: {e}")

    # Filter out None entries and generate reports
    valid_metrics = [m for m in all_metrics if m is not None]
    logging.info(f"Successfully completed {len(valid_metrics)} out of {NUM_RUNS} runs")
    
    summary_csv = os.path.join(EXPERIMENT_DIR, 'summary_statistics.csv')
    generate_summary_table(valid_metrics, summary_csv)

    boxplot_file = os.path.join(EXPERIMENT_DIR, 'metric_boxplots.png')
    plot_comparison_boxplots(valid_metrics, boxplot_file)

    # Export detailed results
    detailed_csv = os.path.join(EXPERIMENT_DIR, 'all_runs_metrics.csv')
    fieldnames = ['run', 'runtime_seconds', 'best_tour_length', 'best_travel_time',
                  'best_waiting_time', 'best_work', 'best_effective_cost', 'has_penalty']
    with open(detailed_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in valid_metrics:
            writer.writerow(m)

    logging.info(f"Experiment complete! Results saved to {EXPERIMENT_DIR}")
    logging.info(f"Summary: {summary_csv}")
    logging.info(f"Boxplots: {boxplot_file}")
    logging.info(f"Detailed metrics: {detailed_csv}")

if __name__ == '__main__':
    main()
