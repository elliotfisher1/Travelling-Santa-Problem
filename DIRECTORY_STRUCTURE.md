# Unified Experiment Directory Structure

All experiment outputs are now organized under a single parent directory for cleaner organization.

## Directory Layout

```
~/Desktop/Dissertation Travelling Santa Problem/
│
├── main_run/
│   │   # Full TSP algorithm with all constraints
│   ├── iteration_metrics.csv
│   ├── final_best_tour.csv
│   ├── final_route_coords.csv
│   ├── convergence_length.png
│   ├── convergence_work.png
│   ├── convergence_travel_time.png
│   ├── triple_convergence.png
│   ├── best_tour.png
│   ├── pheromone_heatmap.png
│   ├── decision_heatmap.png
│   ├── gantt_darkness_chart.png
│   ├── population_coverage.png
│   ├── leg_velocities.png
│   ├── leg_work.png
│   ├── tour_animation.mp4 (if ffmpeg available)
│   ├── pheromone_evolution/
│   │   └── pheromone_iter_*.png (snapshots)
│   └── iteration_*/
│       └── (per-iteration checkpoints)
│
├── distance_only_baseline/
│   │   # Pure TSP (distance minimization only)
│   ├── iteration_metrics_distance_only.csv
│   ├── best_tour_distance_only.csv
│   └── convergence_distance_only.png
│
├── multi_run_experiment/
│   │   # 30 runs with statistical analysis
│   ├── summary_statistics.csv          ← Mean, std, best, worst
│   ├── summary_statistics.txt          ← Human-readable summary
│   ├── all_runs_metrics.csv            ← All run details
│   ├── metric_boxplots.png             ← Distribution plots
│   ├── run_01/
│   │   ├── iteration_metrics.csv
│   │   ├── final_best_tour.csv
│   │   ├── convergence_*.png
│   │   └── ...
│   ├── run_02/
│   │   └── ...
│   └── ... (runs 03-30)
│
├── ant_optimization/
│   │   # Test ant counts: [10, 20, 30, 40, 50, 75, 100]
│   ├── ant_optimization_summary.csv     ← Stats per ant count
│   ├── all_ant_runs.csv                 ← Per-run details
│   ├── work_at_checkpoints.png          ← Work convergence comparison
│   ├── iterations_to_viable.png         ← Convergence speed vs ants
│   ├── runtime_vs_ants.png              ← Computational cost
│   ├── efficiency_metric.png            ← Combined efficiency score
│   ├── RECOMMENDATION.txt               ← Optimal ant count
│   ├── ants_10_run_1/
│   │   ├── iteration_metrics.csv
│   │   └── ...
│   ├── ants_20_run_1/
│   │   └── ...
│   └── ... (all ant count × run combinations)
│
└── city_scaling/
    │   # Test sizes: [10, 15, 20, 25] cities
    ├── city_scaling_summary.csv         ← Stats per city count
    ├── all_city_scaling_runs.csv        ← Per-run details
    ├── scaling_analysis.png             ← Data + curve fits
    │   ├── Power law fit
    │   ├── Exponential fit
    │   └── Quadratic fit
    ├── convergence_curves_by_city_count.png
    ├── ANALYSIS.txt                     ← Fit equations & complexity
    ├── cities_10_run_1/
    │   ├── iteration_metrics.csv
    │   └── ...
    ├── cities_15_run_1/
    │   └── ...
    └── ... (all city count × run combinations)
```

## Key Benefits

✓ **Single parent directory** - All experiments in one place: `~/Desktop/Dissertation Travelling Santa Problem/`

✓ **Clear subdirectories** - Each experiment type has its own folder:
  - `main_run/` - Single main algorithm execution
  - `distance_only_baseline/` - Baseline for comparison
  - `multi_run_experiment/` - Statistical validation
  - `ant_optimization/` - Parameter tuning
  - `city_scaling/` - Scalability analysis

✓ **Easy navigation** - Find results quickly:
  ```bash
  # Go to main results
  cd ~/Desktop/Dissertation\ Travelling\ Santa\ Problem/
  
  # View all runs
  ls */summary*.csv
  
  # Check recommendations
  cat ant_optimization/RECOMMENDATION.txt
  cat city_scaling/ANALYSIS.txt
  ```

✓ **Backup friendly** - Single folder to backup

✓ **Project-wide view** - All experiments visible at a glance

## Directory Creation

The parent directory is automatically created when any experiment runs:
```python
PARENT_EXPERIMENTS_DIR = os.path.expanduser('~/Desktop/Dissertation Travelling Santa Problem')
EXPERIMENT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'subdirectory_name')
```

## Quick Access

### View Summary Statistics
```bash
cd ~/Desktop/Dissertation\ Travelling\ Santa\ Problem/

# Multi-run results
cat multi_run_experiment/summary_statistics.txt

# Ant count recommendations
cat ant_optimization/RECOMMENDATION.txt

# Scaling analysis
cat city_scaling/ANALYSIS.txt
```

### Compare Plots
```bash
# Open all key plots
open */metric*.png
open */iterations*.png
open city_scaling/scaling_analysis.png
```

### Access Detailed Data
```bash
# View all metrics across experiments
ls **/all_*_metrics.csv

# Export to spreadsheet
open multi_run_experiment/all_runs_metrics.csv
```

---

**Updated**: February 16, 2026
