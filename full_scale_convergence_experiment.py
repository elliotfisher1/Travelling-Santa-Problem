"""
Full-Scale Convergence Experiment
==================================
Runs the full TSaP ACO and Distance-Only ACO multiple times each.
Aggregates iteration metrics and creates convergence curves with error bands.

Workflow:
1. Run TSaP ACO N times, collecting iteration_metrics.csv from each
2. Run Distance-Only ACO N times, collecting metrics
3. Calculate mean ± std at each iteration
4. Save aggregated metrics to CSV
5. Generate convergence plots with error bands

Usage:
    python full_scale_convergence_experiment.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
import logging
from typing import Dict, List, Tuple
import importlib.util
import threading

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Ensure logs flush immediately to console
logging.getLogger().handlers[0].flush = lambda: __import__('sys').stdout.flush()

for handler in logging.getLogger().handlers:
    handler.flush()

# --- configuration ---
# Update these paths to match your local output directories

NUM_RUNS_TSAP = 10              # Number of TSaP runs
NUM_RUNS_DISTANCE_ONLY = 10     # Number of Distance-Only runs
NUM_ITERATIONS = 60000          # Iterations per run
NUM_ANTS = 50
PROGRESS_LOG_INTERVAL = 6      # Log progress every N iterations (customizable)
# Output base directory
PARENT_EXPERIMENTS_DIR = os.path.expanduser('~/Desktop/Dissertation Travelling Santa Problem')
EXPERIMENT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'full_scale_convergence_experiment')
OUTPUT_CSV = os.path.join(EXPERIMENT_DIR, 'convergence_metrics_aggregated.csv')
OUTPUT_PLOTS_DIR = os.path.join(EXPERIMENT_DIR, 'plots')

# Python scripts to run
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TSAP_SCRIPT = os.path.join(SCRIPT_DIR, 'main.py')
DISTANCE_ONLY_SCRIPT = os.path.join(SCRIPT_DIR, 'distance_only_aco.py')



def monitor_progress(run_dir: str, variant_name: str, run_num: int, stop_event: threading.Event):
    """
    Background thread that monitors metrics CSV and logs progress every N iterations.
    """
    last_logged_iter = 0
    max_runs = NUM_RUNS_TSAP if 'TSaP' in variant_name else NUM_RUNS_DISTANCE_ONLY
    
    # Find the metrics CSV file
    metrics_csv = None
    wait_count = 0
    while not metrics_csv and wait_count < 10:
        for fname in os.listdir(run_dir):
            if 'iteration_metrics' in fname and fname.endswith('.csv'):
                metrics_csv = os.path.join(run_dir, fname)
                break
        if not metrics_csv:
            wait_count += 1
            time.sleep(0.5)
    
    if not metrics_csv:
        return
    
    # Monitor the CSV file
    while not stop_event.is_set():
        try:
            df = pd.read_csv(metrics_csv)
            if len(df) > 0:
                current_iter = df['Iteration'].iloc[-1]
                
                # Log every PROGRESS_LOG_INTERVAL iterations
                if current_iter >= last_logged_iter + PROGRESS_LOG_INTERVAL:
                    last_row = df.iloc[-1]
                    
                    # Extract metrics
                    dist_val = 'Unknown'
                    work_val = 'Unknown'
                    for col in df.columns:
                        if 'length' in col.lower() or 'distance' in col.lower():
                            dist_val = f"{last_row[col]:.0f}"
                        if 'work' in col.lower() and 'j' in col.lower():
                            work_val = f"{last_row[col]:.2e}"
                    
                    logging.info(f"  [{variant_name} {run_num}/{max_runs}] Iter {int(current_iter)}: Distance={dist_val} km, Work={work_val} J")
                    last_logged_iter = int(current_iter)
        except:
            pass
        
        time.sleep(1)  # Check every second


def create_directories():

    """Create necessary output directories."""
    os.makedirs(EXPERIMENT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_PLOTS_DIR, exist_ok=True)
    logging.info(f"Output directory: {EXPERIMENT_DIR}")


def run_algorithm_variant(script_path: str, variant_name: str, run_num: int, 
                         output_dir: str, num_iterations: int) -> Dict:
    """
    Run a single instance of TSaP or Distance-Only ACO.
    Returns path to iteration_metrics.csv and runtime.
    """
    run_dir = os.path.join(output_dir, f'{variant_name.lower()}_run_{run_num:02d}')
    os.makedirs(run_dir, exist_ok=True)
    
    max_runs = NUM_RUNS_TSAP if 'TSaP' in variant_name else NUM_RUNS_DISTANCE_ONLY
    logging.info(f"\n{'='*80}")
    logging.info(f"[{variant_name} Run {run_num}/{max_runs}] Starting...")
    logging.info(f"Output: {run_dir}")
    logging.info(f"{'='*80}")
    
    # Read the script
    with open(script_path, 'r') as f:
        code = f.read()
    
    # Modify parameters - use simple string replacements (faster than line-by-line)
    code = code.replace(
        "MAIN_OUTPUT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'main_run')",
        f"MAIN_OUTPUT_DIR = r'{run_dir}'"
    )
    code = code.replace(
        "MAIN_OUTPUT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'main_run_4 ')",
        f"MAIN_OUTPUT_DIR = r'{run_dir}'"
    )
    code = code.replace(
        "MAIN_OUTPUT_DIR = os.path.join(os.path.expanduser('~/Desktop/Dissertation Travelling Santa Problem'), 'distance_only')",
        f"MAIN_OUTPUT_DIR = r'{run_dir}'"
    )
    code = code.replace("NUM_ITERATIONS = 6000", f"NUM_ITERATIONS = {num_iterations}")
    code = code.replace("NUM_ITERATIONS = 60000", f"NUM_ITERATIONS = {num_iterations}")
    code = code.replace("NUM_ANTS = 50", f"NUM_ANTS = {NUM_ANTS}")
    code = code.replace("NUM_ANTS = 14", f"NUM_ANTS = {NUM_ANTS}")
    
    # Execute with background monitoring
    start_time = time.time()
    stop_monitoring = threading.Event()
    
    # Start background progress monitor
    monitor_thread = threading.Thread(
        target=monitor_progress,
        args=(run_dir, variant_name, run_num, stop_monitoring),
        daemon=True
    )
    monitor_thread.start()
    
    try:
        exec_globals = {'__name__': '__main__'}
        exec(code, exec_globals)
        runtime = time.time() - start_time
        
        # Stop monitoring
        stop_monitoring.set()
        monitor_thread.join(timeout=2)
        
        # Monitor and log progress from metrics CSV
        metrics_csv_path = os.path.join(run_dir, 'iteration_metrics.csv')
        if os.path.exists(metrics_csv_path):
            try:
                df = pd.read_csv(metrics_csv_path)
                if len(df) > 0:
                    last_row = df.iloc[-1]
                    iteration = last_row.get('Iteration', 'Unknown')
                    
                    # Try to find distance and work columns
                    dist_val = 'Unknown'
                    work_val = 'Unknown'
                    for col in df.columns:
                        if 'length' in col.lower() or 'distance' in col.lower():
                            dist_val = f"{last_row[col]:.2f}"
                        if 'work' in col.lower() and 'j' in col.lower():
                            work_val = f"{last_row[col]:.2e}"
                    
                    logging.info(f"    Final metrics - Iteration {iteration}: Distance={dist_val} km, Work={work_val} J")
            except:
                pass
        
        # Find metrics CSV
        metrics_csv = None
        for fname in os.listdir(run_dir):
            if 'iteration_metrics' in fname and fname.endswith('.csv'):
                metrics_csv = os.path.join(run_dir, fname)
                break
        
        if not metrics_csv:
            logging.error(f"    ✗ No iteration_metrics.csv found in {run_dir}")
            return None
        
        # Verify file exists and has content (don't read entire CSV - too slow)
        file_size = os.path.getsize(metrics_csv)
        if file_size < 100:  # CSV header is ~100 bytes, so if smaller it's empty
            logging.error(f"    ✗ iteration_metrics.csv is empty in {run_dir}")
            return None
        
        logging.info(f"    ✓ Saved iteration_metrics.csv ({file_size} bytes) to {run_dir}")
        logging.info(f"    ✓ Completed in {runtime:.1f}s")
        return {'metrics_csv': metrics_csv, 'runtime': runtime, 'run_dir': run_dir}
        
    except Exception as e:
        logging.error(f"    Error during execution: {e}")
        return None


def load_iteration_metrics(csv_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load distance and work metrics from CSV.
    Returns: (distance_array, work_array)
    """
    try:
        df = pd.read_csv(csv_path)
        
        # Find distance column
        distance_col = None
        work_col = None
        
        for col in df.columns:
            if 'length' in col.lower() or 'distance' in col.lower():
                distance_col = col
            if 'work' in col.lower() and 'j' in col.lower():
                work_col = col
        
        if not distance_col or not work_col:
            logging.error(f"  Could not find distance/work columns in {csv_path}")
            return None, None
        
        return df[distance_col].values, df[work_col].values
        
    except Exception as e:
        logging.error(f"  Error loading {csv_path}: {e}")
        return None, None


def aggregate_metrics(runs: List[Dict], variant_name: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Aggregate metrics across multiple runs.
    Returns: (iterations, distance_mean, distance_std, work_mean, work_std)
    """
    distances = []
    works = []
    num_iters = 0
    
    for run_data in runs:
        if not run_data:
            continue
        
        dist, work = load_iteration_metrics(run_data['metrics_csv'])
        if dist is None:
            continue
        
        distances.append(dist)
        works.append(work)
        num_iters = max(num_iters, len(dist))
    
    if not distances:
        logging.error(f"No valid runs for {variant_name}")
        return None, None, None, None, None
    
    # Pad arrays to same length
    for i, dist in enumerate(distances):
        if len(dist) < num_iters:
            distances[i] = np.pad(dist, (0, num_iters - len(dist)), mode='edge')
    
    for i, work in enumerate(works):
        if len(work) < num_iters:
            works[i] = np.pad(work, (0, num_iters - len(work)), mode='edge')
    
    distances = np.array(distances)
    works = np.array(works)
    
    iterations = np.arange(num_iters)
    distance_mean = np.mean(distances, axis=0)
    distance_std = np.std(distances, axis=0)
    work_mean = np.mean(works, axis=0)
    work_std = np.std(works, axis=0)
    
    logging.info(f"{variant_name}: {len(distances)} runs aggregated")
    logging.info(f"  Final distance: {distance_mean[-1]:.2f} ± {distance_std[-1]:.2f} km")
    logging.info(f"  Final work: {work_mean[-1]:.2e} ± {work_std[-1]:.2e} J")
    
    return iterations, distance_mean, distance_std, work_mean, work_std


def save_aggregated_csv(tsap_data: Dict, distance_data: Dict, output_csv: str):
    """Save aggregated metrics to CSV."""
    iterations = tsap_data['iterations']
    
    df = pd.DataFrame({
        'Iteration': iterations,
        'TSaP_Distance_Mean_km': tsap_data['distance_mean'],
        'TSaP_Distance_Std_km': tsap_data['distance_std'],
        'TSaP_Work_Mean_J': tsap_data['work_mean'],
        'TSaP_Work_Std_J': tsap_data['work_std'],
        'DistanceOnly_Distance_Mean_km': distance_data['distance_mean'],
        'DistanceOnly_Distance_Std_km': distance_data['distance_std'],
        'DistanceOnly_Work_Mean_J': distance_data['work_mean'],
        'DistanceOnly_Work_Std_J': distance_data['work_std'],
    })
    
    df.to_csv(output_csv, index=False)
    logging.info(f"\n✓ Saved aggregated metrics to {output_csv}")


def plot_convergence_comparison(tsap_data: Dict, distance_data: Dict, output_dir: str):
    """Generate convergence plots comparing TSaP vs Distance-Only."""
    iters = tsap_data['iterations']
    
    # Plot 1: Side-by-side Distance
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # TSaP Distance
    ax1.fill_between(
        iters,
        tsap_data['distance_mean'] - tsap_data['distance_std'],
        tsap_data['distance_mean'] + tsap_data['distance_std'],
        alpha=0.3, color='#FF6B6B', label='±1 Std Dev'
    )
    ax1.plot(iters, tsap_data['distance_mean'], color='#CC0000', linewidth=2.8, label='TSaP')
    ax1.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
    ax1.set_title('Distance Convergence - TSaP', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor('white')
    
    # Distance-Only Distance
    ax2.fill_between(
        iters,
        distance_data['distance_mean'] - distance_data['distance_std'],
        distance_data['distance_mean'] + distance_data['distance_std'],
        alpha=0.3, color='#FF9999', label='±1 Std Dev'
    )
    ax2.plot(iters, distance_data['distance_mean'], color='#AA0000', linewidth=2.8, label='Distance-Only')
    ax2.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
    ax2.set_title('Distance Convergence - Distance-Only', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor('white')
    
    plt.suptitle('Distance Convergence Comparison', fontsize=14, fontweight='bold')
    fig.patch.set_facecolor('white')
    fig.tight_layout()
    
    output_file = os.path.join(output_dir, '01_distance_convergence_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    logging.info(f"✓ Saved {output_file}")
    plt.close()
    
    # Plot 2: Side-by-side Work
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # TSaP Work
    ax1.fill_between(
        iters,
        tsap_data['work_mean'] - tsap_data['work_std'],
        tsap_data['work_mean'] + tsap_data['work_std'],
        alpha=0.3, color='#4ECDC4', label='±1 Std Dev'
    )
    ax1.plot(iters, tsap_data['work_mean'], color='#0088AA', linewidth=2.8, label='TSaP')
    ax1.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Work (Joules)', fontsize=12, fontweight='bold')
    ax1.set_title('Work Convergence - TSaP', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=11)
    ax1.grid(True, alpha=0.3)
    ax1.set_facecolor('white')
    
    # Distance-Only Work
    ax2.fill_between(
        iters,
        distance_data['work_mean'] - distance_data['work_std'],
        distance_data['work_mean'] + distance_data['work_std'],
        alpha=0.3, color='#88E5DD', label='±1 Std Dev'
    )
    ax2.plot(iters, distance_data['work_mean'], color='#006688', linewidth=2.8, label='Distance-Only')
    ax2.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Work (Joules)', fontsize=12, fontweight='bold')
    ax2.set_title('Work Convergence - Distance-Only', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=11)
    ax2.grid(True, alpha=0.3)
    ax2.set_facecolor('white')
    
    plt.suptitle('Work Convergence Comparison', fontsize=14, fontweight='bold')
    fig.patch.set_facecolor('white')
    fig.tight_layout()
    
    output_file = os.path.join(output_dir, '02_work_convergence_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    logging.info(f"✓ Saved {output_file}")
    plt.close()
    
    # Plot 3: Dual-axis overlay TSaP
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    ax1.fill_between(
        iters,
        tsap_data['distance_mean'] - tsap_data['distance_std'],
        tsap_data['distance_mean'] + tsap_data['distance_std'],
        alpha=0.3, color='#FF6B6B'
    )
    ax1.plot(iters, tsap_data['distance_mean'], color='#CC0000', linewidth=2.8, label='Distance')
    ax1.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Distance (km)', fontsize=12, fontweight='bold', color='#CC0000')
    ax1.tick_params(axis='y', labelcolor='#CC0000')
    ax1.grid(True, alpha=0.3)
    
    ax2 = ax1.twinx()
    ax2.fill_between(
        iters,
        tsap_data['work_mean'] - tsap_data['work_std'],
        tsap_data['work_mean'] + tsap_data['work_std'],
        alpha=0.3, color='#4ECDC4'
    )
    ax2.plot(iters, tsap_data['work_mean'], color='#0088AA', linewidth=2.8, label='Work')
    ax2.set_ylabel('Work (Joules)', fontsize=12, fontweight='bold', color='#0088AA')
    ax2.tick_params(axis='y', labelcolor='#0088AA')
    
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=11, loc='upper right')
    
    ax1.set_facecolor('white')
    fig.patch.set_facecolor('white')
    plt.title('TSaP Dual-Axis Convergence (Distance + Work)', fontsize=14, fontweight='bold', pad=15)
    fig.tight_layout()
    
    output_file = os.path.join(output_dir, '03_tsap_dualaxis.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    logging.info(f"✓ Saved {output_file}")
    plt.close()


def main():
    """Main execution."""
    logging.info("=" * 80)
    logging.info("FULL-SCALE CONVERGENCE EXPERIMENT")
    logging.info("=" * 80)
    logging.info(f"\nRunning {NUM_RUNS_TSAP} TSaP runs and {NUM_RUNS_DISTANCE_ONLY} Distance-Only runs")
    logging.info(f"Iterations per run: {NUM_ITERATIONS}\n")
    
    create_directories()
    
    # === RUN TSaP ACO ===
    logging.info("PHASE 1: Running TSaP ACO")
    logging.info("-" * 80)
    tsap_runs = []
    for i in range(1, NUM_RUNS_TSAP + 1):
        result = run_algorithm_variant(TSAP_SCRIPT, 'TSaP', i, EXPERIMENT_DIR, NUM_ITERATIONS)
        tsap_runs.append(result)
    
    # === RUN DISTANCE-ONLY ACO ===
    logging.info("\nPHASE 2: Running Distance-Only ACO")
    logging.info("-" * 80)
    distance_runs = []
    for i in range(1, NUM_RUNS_DISTANCE_ONLY + 1):
        result = run_algorithm_variant(DISTANCE_ONLY_SCRIPT, 'DistanceOnly', i, EXPERIMENT_DIR, NUM_ITERATIONS)
        distance_runs.append(result)
    
    # === AGGREGATE METRICS ===
    logging.info("\nPHASE 3: Aggregating Metrics")
    logging.info("-" * 80)
    
    iters, tsap_dist_mean, tsap_dist_std, tsap_work_mean, tsap_work_std = \
        aggregate_metrics(tsap_runs, 'TSaP')
    
    _, dist_dist_mean, dist_dist_std, dist_work_mean, dist_work_std = \
        aggregate_metrics(distance_runs, 'Distance-Only')
    
    if iters is None:
        logging.error("Failed to aggregate metrics!")
        return
    
    # === SAVE CSV ===
    logging.info("\nPHASE 4: Saving Aggregated Data")
    logging.info("-" * 80)
    
    tsap_data = {
        'iterations': iters,
        'distance_mean': tsap_dist_mean,
        'distance_std': tsap_dist_std,
        'work_mean': tsap_work_mean,
        'work_std': tsap_work_std,
    }
    
    distance_data = {
        'iterations': iters,
        'distance_mean': dist_dist_mean,
        'distance_std': dist_dist_std,
        'work_mean': dist_work_mean,
        'work_std': dist_work_std,
    }
    
    save_aggregated_csv(tsap_data, distance_data, OUTPUT_CSV)
    
    # === GENERATE PLOTS ===
    logging.info("\nPHASE 5: Generating Plots")
    logging.info("-" * 80)
    plot_convergence_comparison(tsap_data, distance_data, OUTPUT_PLOTS_DIR)
    
    logging.info("\n" + "=" * 80)
    logging.info("✓ EXPERIMENT COMPLETE")
    logging.info("=" * 80)
    logging.info(f"\nOutput CSV: {OUTPUT_CSV}")
    logging.info(f"Output Plots: {OUTPUT_PLOTS_DIR}")


if __name__ == '__main__':
    main()
