"""
Convergence Curves with Error Bars (Multi-Run Stats Applied to Full TSaP Run)
==============================================================================
Takes statistical measurements (std dev) from multi-run experiment and applies them
as error bands to the full-scale TSaP Output convergence curve.

This shows how the full-scale run compares to the statistical variability from multiple runs.

Usage:
    python convergence_with_error_bars.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==============================================================================
# Configuration
# ==============================================================================

# Multi-run experiment (source of statistics)
MULTI_RUN_DIR = '/Users/elliotfisher/Desktop/Dissertation Travelling Santa Problem/multi_run_experiment'

# Full-scale TSaP run (where to apply error bands)
TSAP_OUTPUT_DIR = '/Users/elliotfisher/Downloads/TSaP with 14 Ants 60,000'
TSAP_METRICS_CSV = os.path.join(TSAP_OUTPUT_DIR, 'iteration_metrics.csv')

# Output directory for plots
OUTPUT_DIR = TSAP_OUTPUT_DIR

# ==============================================================================
# Core Functions
# ==============================================================================

def extract_multirun_statistics(experiment_dir: str) -> Tuple[np.ndarray, Dict[str, np.ndarray]]:
    """
    Extract statistical measurements from multi-run experiment.
    Returns: (iterations, stats_dict) where stats_dict has 'distance_std', 'work_std', etc.
    """
    run_dirs = []
    
    # Find all run directories
    for entry in sorted(os.listdir(experiment_dir)):
        run_path = os.path.join(experiment_dir, entry)
        if os.path.isdir(run_path) and (entry.startswith('run_') or entry.startswith('ants_')):
            run_dirs.append(run_path)
    
    logging.info(f"Found {len(run_dirs)} multi-run directories for statistics")
    
    if not run_dirs:
        raise FileNotFoundError(f"No run directories found in {experiment_dir}")
    
    distance_arrays = []
    work_arrays = []
    max_iters = 0
    
    for i, run_dir in enumerate(run_dirs):
        metrics_csv = os.path.join(run_dir, 'iteration_metrics.csv')
        
        if not os.path.exists(metrics_csv):
            logging.warning(f"  Skipping {run_dir}: iteration_metrics.csv not found")
            continue
        
        try:
            df = pd.read_csv(metrics_csv)
            
            # Find column names
            distance_col = None
            work_col = None
            
            for col in df.columns:
                if 'length' in col.lower() or 'distance' in col.lower():
                    distance_col = col
                if 'work' in col.lower() and 'j' in col.lower():
                    work_col = col
            
            if distance_col:
                distance_arrays.append(df[distance_col].values)
                max_iters = max(max_iters, len(df))
            if work_col:
                work_arrays.append(df[work_col].values)
            
            logging.info(f"  Run {i+1}: Loaded {len(df)} iterations")
            
        except Exception as e:
            logging.error(f"  Error loading {metrics_csv}: {e}")
    
    # Pad arrays to same length
    def pad_arrays(arrays, target_len):
        padded = []
        for arr in arrays:
            if len(arr) < target_len:
                arr = np.pad(arr, (0, target_len - len(arr)), mode='edge')
            padded.append(arr)
        return np.array(padded)
    
    distance_data = pad_arrays(distance_arrays, max_iters)
    work_data = pad_arrays(work_arrays, max_iters)
    
    # Calculate statistics
    distance_std = np.std(distance_data, axis=0)
    work_std = np.std(work_data, axis=0)
    distance_mean = np.mean(distance_data, axis=0)
    work_mean = np.mean(work_data, axis=0)
    
    iterations = np.arange(max_iters)
    
    stats = {
        'distance_std': distance_std,
        'distance_mean': distance_mean,
        'work_std': work_std,
        'work_mean': work_mean,
    }
    
    return iterations, stats


def load_tsap_metrics(csv_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Load the full-scale TSaP run metrics.
    Returns: (iterations, distance, work)
    """
    df = pd.read_csv(csv_path)
    
    # Find column names
    distance_col = None
    work_col = None
    
    for col in df.columns:
        if 'length' in col.lower() or 'distance' in col.lower():
            distance_col = col
        if 'work' in col.lower() and 'j' in col.lower():
            work_col = col
    
    if not distance_col or not work_col:
        raise ValueError(f"Could not find distance and work columns in {csv_path}")
    
    iterations = df['Iteration'].values if 'Iteration' in df.columns else np.arange(len(df))
    distance = df[distance_col].values
    work = df[work_col].values
    
    logging.info(f"Loaded TSaP metrics: {len(distance)} iterations")
    
    return iterations, distance, work


def plot_tsap_with_multirun_bands(
    iterations: np.ndarray,
    tsap_distance: np.ndarray,
    tsap_work: np.ndarray,
    multirun_stats: Dict[str, np.ndarray],
    output_path: str
) -> None:
    """
    Plot TSaP full-scale run with uncertainty bands from multi-run experiment.
    Shows TSaP curve with shaded uncertainty regions around it.
    Extends uncertainty bands to match full iteration length.
    """
    fig, (ax_dist, ax_work) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Extend uncertainty bands to match full TSaP length by padding
    iters = iterations
    tsap_dist = tsap_distance
    tsap_w = tsap_work
    
    # Pad uncertainty arrays to match full length
    multi_dist_std = multirun_stats['distance_std']
    multi_work_std = multirun_stats['work_std']
    
    if len(multi_dist_std) < len(iters):
        # Extend by padding with the last value
        multi_dist_std = np.pad(multi_dist_std, (0, len(iters) - len(multi_dist_std)), mode='edge')
        multi_work_std = np.pad(multi_work_std, (0, len(iters) - len(multi_work_std)), mode='edge')
    else:
        # Trim to match
        multi_dist_std = multi_dist_std[:len(iters)]
        multi_work_std = multi_work_std[:len(iters)]
    
    # Distance plot - TSaP with uncertainty band
    ax_dist.fill_between(
        iters,
        tsap_dist - multi_dist_std,
        tsap_dist + multi_dist_std,
        alpha=0.3, color='#FF6B6B', label='±1 Std Dev'
    )
    ax_dist.plot(iters, tsap_dist, color='#CC0000', linewidth=2.8, 
                 label='TSaP Distance')
    
    ax_dist.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax_dist.set_ylabel('Distance (km)', fontsize=12, fontweight='bold')
    ax_dist.set_title('Distance Convergence', fontsize=13, fontweight='bold')
    ax_dist.legend(fontsize=11, loc='upper right', framealpha=0.95)
    ax_dist.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_dist.set_facecolor('white')
    
    # Work plot - TSaP with uncertainty band
    ax_work.fill_between(
        iters,
        tsap_w - multi_work_std,
        tsap_w + multi_work_std,
        alpha=0.3, color='#4ECDC4', label='±1 Std Dev'
    )
    ax_work.plot(iters, tsap_w, color='#0088AA', linewidth=2.8, 
                 label='TSaP Work')
    
    ax_work.set_xlabel('Iteration', fontsize=12, fontweight='bold')
    ax_work.set_ylabel('Work (Joules)', fontsize=12, fontweight='bold')
    ax_work.set_title('Work Convergence', fontsize=13, fontweight='bold')
    ax_work.legend(fontsize=11, loc='upper right', framealpha=0.95)
    ax_work.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax_work.set_facecolor('white')
    
    plt.suptitle('Full-Scale TSaP Run with Multi-Run Uncertainty Bands', 
                 fontsize=14, fontweight='bold', y=0.98)
    fig.patch.set_facecolor('white')
    fig.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    logging.info(f"✓ Saved TSaP comparison plot to {output_path}")
    plt.close()


def plot_tsap_dualaxis_with_bands(
    iterations: np.ndarray,
    tsap_distance: np.ndarray,
    tsap_work: np.ndarray,
    multirun_stats: Dict[str, np.ndarray],
    output_path: str
) -> None:
    """
    Dual-axis plot: TSaP run with uncertainty bands on single plot.
    Matches the style of the reference chart (solid lines + uncertainty bands).
    Extends uncertainty bands to match full iteration length.
    """
    fig, ax1 = plt.subplots(figsize=(14, 7))
    
    # Use full TSaP iteration length
    iters = iterations
    tsap_dist = tsap_distance
    tsap_w = tsap_work
    
    # Pad uncertainty arrays to match full length
    multi_dist_std = multirun_stats['distance_std']
    multi_work_std = multirun_stats['work_std']
    
    if len(multi_dist_std) < len(iters):
        # Extend by padding with the last value
        multi_dist_std = np.pad(multi_dist_std, (0, len(iters) - len(multi_dist_std)), mode='edge')
        multi_work_std = np.pad(multi_work_std, (0, len(iters) - len(multi_work_std)), mode='edge')
    else:
        # Trim to match
        multi_dist_std = multi_dist_std[:len(iters)]
        multi_work_std = multi_work_std[:len(iters)]
    
    # === LEFT AXIS: DISTANCE (RED) ===
    ax1.fill_between(
        iters,
        tsap_dist - multi_dist_std,
        tsap_dist + multi_dist_std,
        alpha=0.3, color='#FF6B6B', label='Distance ±1 Std Dev'
    )
    ax1.plot(
        iters, tsap_dist, 
        color='#CC0000', linewidth=2.8, label='TSaP (Distance)',
        marker=None
    )
    ax1.set_xlabel('Iteration', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Distance (km)', fontsize=13, fontweight='bold', color='#CC0000')
    ax1.tick_params(axis='y', labelcolor='#CC0000', labelsize=11)
    ax1.tick_params(axis='x', labelsize=11)
    ax1.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    
    # === RIGHT AXIS: WORK (BLUE) ===
    ax2 = ax1.twinx()
    ax2.fill_between(
        iters,
        tsap_w - multi_work_std,
        tsap_w + multi_work_std,
        alpha=0.3, color='#4ECDC4', label='Work ±1 Std Dev'
    )
    ax2.plot(
        iters, tsap_w, 
        color='#0088AA', linewidth=2.8, label='TSaP (Work)',
        marker=None
    )
    ax2.set_ylabel('Work (Joules)', fontsize=13, fontweight='bold', color='#0088AA')
    ax2.tick_params(axis='y', labelcolor='#0088AA', labelsize=11)
    
    # === LEGEND ===
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, fontsize=12, loc='upper right', 
               framealpha=0.95, edgecolor='gray')
    
    # === STYLING ===
    ax1.set_facecolor('white')
    fig.patch.set_facecolor('white')
    
    plt.title('Full-Scale TSaP Run with Multi-Run Uncertainty Bands', 
              fontsize=15, fontweight='bold', pad=20)
    fig.tight_layout()
    
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
    logging.info(f"✓ Saved dual-axis plot to {output_path}")
    plt.close()


def generate_error_statistics_csv(
    iterations: np.ndarray,
    tsap_distance: np.ndarray,
    tsap_work: np.ndarray,
    multirun_stats: Dict[str, np.ndarray],
    output_path: str
) -> None:
    """
    Save iteration statistics comparing TSaP to multi-run bands.
    Extends uncertainty bands to match full length if needed.
    """
    # Pad uncertainty arrays to match full length
    multi_dist_std = multirun_stats['distance_std']
    multi_work_std = multirun_stats['work_std']
    
    if len(multi_dist_std) < len(iterations):
        multi_dist_std = np.pad(multi_dist_std, (0, len(iterations) - len(multi_dist_std)), mode='edge')
        multi_work_std = np.pad(multi_work_std, (0, len(iterations) - len(multi_work_std)), mode='edge')
    else:
        multi_dist_std = multi_dist_std[:len(iterations)]
        multi_work_std = multi_work_std[:len(iterations)]
    
    stats_df = pd.DataFrame({
        'Iteration': iterations,
        'TSaP_Distance_km': tsap_distance,
        'MultiRun_Distance_Std_km': multi_dist_std,
        'TSaP_Work_J': tsap_work,
        'MultiRun_Work_Std_J': multi_work_std,
    })
    
    stats_df.to_csv(output_path, index=False)
    logging.info(f"✓ Saved statistics comparison to {output_path}")


def main() -> None:
    """
    Main execution: Apply multi-run statistics to full-scale TSaP run.
    """
    logging.info("=" * 80)
    logging.info("FULL-SCALE TSaP WITH MULTI-RUN ERROR BANDS")
    logging.info("=" * 80)
    
    # Verify paths exist
    if not os.path.exists(MULTI_RUN_DIR):
        logging.error(f"Multi-run directory not found: {MULTI_RUN_DIR}")
        return
    
    if not os.path.exists(TSAP_METRICS_CSV):
        logging.error(f"TSaP metrics file not found: {TSAP_METRICS_CSV}")
        return
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    logging.info(f"\nMulti-run Directory: {MULTI_RUN_DIR}")
    logging.info(f"TSaP Metrics: {TSAP_METRICS_CSV}")
    logging.info(f"Output Directory: {OUTPUT_DIR}\n")
    
    # Extract statistics from multi-run experiment
    logging.info("Extracting statistical measurements from multi-run experiment...")
    try:
        multirun_iters, multirun_stats = extract_multirun_statistics(MULTI_RUN_DIR)
    except Exception as e:
        logging.error(f"Error extracting multi-run statistics: {e}")
        return
    
    logging.info(f"  Multi-run statistics: {len(multirun_iters)} iterations")
    logging.info(f"    Distance std: {multirun_stats['distance_std'][-1]:.2f} km")
    logging.info(f"    Work std: {multirun_stats['work_std'][-1]:.2e} J")
    
    # Load TSaP full-scale metrics
    logging.info("\nLoading full-scale TSaP run metrics...")
    try:
        tsap_iters, tsap_distance, tsap_work = load_tsap_metrics(TSAP_METRICS_CSV)
    except Exception as e:
        logging.error(f"Error loading TSaP metrics: {e}")
        return
    
    logging.info(f"  TSaP run: {len(tsap_iters)} iterations")
    logging.info(f"    Final distance: {tsap_distance[-1]:.2f} km")
    logging.info(f"    Final work: {tsap_work[-1]:.2e} J")
    
    # Generate plots
    logging.info("\nGenerating visualizations...\n")
    
    # Plot 1: Side-by-side comparison
    output_1 = os.path.join(OUTPUT_DIR, '01_convergence_sidebyside.png')
    plot_tsap_with_multirun_bands(
        tsap_iters, tsap_distance, tsap_work, multirun_stats, output_1
    )
    
    # Plot 2: Dual-axis comparison
    output_2 = os.path.join(OUTPUT_DIR, '02_convergence_dualaxis.png')
    plot_tsap_dualaxis_with_bands(
        tsap_iters, tsap_distance, tsap_work, multirun_stats, output_2
    )
    
    # Save statistics to CSV
    output_csv = os.path.join(OUTPUT_DIR, 'tsap_with_multirun_bands.csv')
    generate_error_statistics_csv(tsap_iters, tsap_distance, tsap_work, multirun_stats, output_csv)
    
    logging.info("=" * 80)
    logging.info(f"✓ ALL PLOTS GENERATED SUCCESSFULLY")
    logging.info("=" * 80)
    logging.info("\nGenerated Files:")
    logging.info(f"  1. {output_1}")
    logging.info(f"  2. {output_2}")
    logging.info(f"  3. {output_csv}")
    logging.info("\nThese plots show the full-scale TSaP run compared to the")
    logging.info("statistical uncertainty bands from the multi-run experiment.")


if __name__ == '__main__':
    main()
