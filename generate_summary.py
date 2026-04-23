#!/usr/bin/env python3
import os
import json
import csv
import numpy as np
from pathlib import Path

EXPERIMENT_DIR = os.path.expanduser('~/Desktop/Dissertation Travelling Santa Problem/multi_run_experiment')
all_metrics = []

print("Collecting metrics from successful runs...")
for run_num in range(1, 16):
    run_dir = os.path.join(EXPERIMENT_DIR, f'run_{run_num:02d}')
    metrics_file = os.path.join(run_dir, 'metrics.json')
    
    if os.path.exists(metrics_file):
        try:
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
                all_metrics.append(metrics)
                print(f"  ✓ Run {run_num}: {metrics['best_tour_length']:.2f} km")
        except Exception as e:
            print(f"  ✗ Run {run_num}: Error reading metrics - {e}")
    else:
        print(f"  ✗ Run {run_num}: No metrics file found")

print(f"\n✓ Successfully loaded {len(all_metrics)} runs out of 15\n")

if len(all_metrics) > 0:
    # Extract metrics
    tour_lengths = [m['best_tour_length'] for m in all_metrics]
    travel_times = [m['best_travel_time'] for m in all_metrics]
    works = [m['best_work'] for m in all_metrics]
    eff_costs = [m['best_effective_cost'] for m in all_metrics]
    runtimes = [m['runtime_seconds'] for m in all_metrics]
    
    # Generate summary
    summary_txt = os.path.join(EXPERIMENT_DIR, 'summary_statistics.txt')
    with open(summary_txt, 'w') as f:
        f.write("=" * 80 + "\n")
        f.write("EXPERIMENT SUMMARY\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Runs Completed: {len(all_metrics)} / 15\n\n")
        
        summary_data = {
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
        
        # Write table
        f.write(f"{'Metric':<25} {'Mean':>12} {'Std Dev':>12} {'Best':>12} {'Worst':>12}\n")
        f.write("-" * 75 + "\n")
        for i, metric in enumerate(summary_data['Metric']):
            f.write(f"{metric:<25} {summary_data['Mean'][i]:>12.2f} {summary_data['Std Dev'][i]:>12.2f} {summary_data['Best'][i]:>12.2f} {summary_data['Worst'][i]:>12.2f}\n")
    
    # Generate CSV
    summary_csv = os.path.join(EXPERIMENT_DIR, 'summary_statistics.csv')
    with open(summary_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Metric', 'Mean', 'Std Dev', 'Best', 'Worst'])
        writer.writeheader()
        for i, metric in enumerate(summary_data['Metric']):
            writer.writerow({
                'Metric': metric,
                'Mean': f"{summary_data['Mean'][i]:.2f}",
                'Std Dev': f"{summary_data['Std Dev'][i]:.2f}",
                'Best': f"{summary_data['Best'][i]:.2f}",
                'Worst': f"{summary_data['Worst'][i]:.2f}"
            })
    
    # Generate detailed CSV
    detailed_csv = os.path.join(EXPERIMENT_DIR, 'all_runs_metrics.csv')
    fieldnames = ['run', 'runtime_seconds', 'best_tour_length', 'best_travel_time',
                  'best_waiting_time', 'best_work', 'best_effective_cost', 'has_penalty']
    with open(detailed_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for i, m in enumerate(all_metrics, 1):
            writer.writerow({
                'run': i,
                'runtime_seconds': m.get('runtime_seconds', ''),
                'best_tour_length': m.get('best_tour_length', ''),
                'best_travel_time': m.get('best_travel_time', ''),
                'best_waiting_time': m.get('best_waiting_time', ''),
                'best_work': m.get('best_work', ''),
                'best_effective_cost': m.get('best_effective_cost', ''),
                'has_penalty': m.get('has_penalty', '')
            })
    
    # Print summary to console
    print("SUMMARY STATISTICS (from 14 successful runs):")
    print("-" * 75)
    print(f"{'Metric':<25} {'Mean':>12} {'Std Dev':>12} {'Best':>12} {'Worst':>12}")
    print("-" * 75)
    for i, metric in enumerate(summary_data['Metric']):
        print(f"{metric:<25} {summary_data['Mean'][i]:>12.2f} {summary_data['Std Dev'][i]:>12.2f} {summary_data['Best'][i]:>12.2f} {summary_data['Worst'][i]:>12.2f}")
    
    print(f"\n✓ Summary files saved to {EXPERIMENT_DIR}")
else:
    print("✗ No successful runs found!")
