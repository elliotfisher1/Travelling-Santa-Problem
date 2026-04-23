# Travelling Santa Problem - Comprehensive ACO Experiment Suite

A complete research framework for analyzing Ant Colony Optimization applied to the Travelling Santa Problem (TSP variant with darkness constraints). This suite includes the main algorithm, multiple baselines, and comprehensive experimental analyses.

## Project Overview

The **Travelling Santa Problem** adds real-world constraints to the classic Travelling Salesman Problem:
- Santa must visit each city **during local darkness** (night-time delivery)
- Route optimization must balance:
  - Distance minimization
  - Travel time constraints
  - Physical work/energy cost (drag model)
  - Daylight availability windows
  - Population coverage

## Files and Modules

### Core Algorithm
- **`main.py`** - Full TSP algorithm with all constraints
  - Implements Ant Colony Optimization
  - Includes per-iteration metrics CSV logging
  - Generates comprehensive visualizations
  - Outputs: convergence curves, Gantt charts, tour maps, heatmaps, animations

### Baseline Implementations
- **`distance_only_aco.py`** - Distance-minimization-only baseline
  - Pure TSP without darkness constraints
  - Serves as comparison baseline for full algorithm
  - Simpler objective function for validation

### Experiment Runners

#### 1. Multi-Run Experiment (`experiment_runner.py`)
**Purpose**: Statistical validation across multiple runs

**Features**:
- Runs full algorithm 30 times
- Records comprehensive metrics from each run
- Generates summary statistics (mean, std dev, best, worst)
- Creates boxplots and comparative visualizations
- Outputs:
  - `summary_statistics.csv` - Mean/std/best/worst for all metrics
  - `metric_boxplots.png` - Distribution visualizations
  - `all_runs_metrics.csv` - Detailed per-run data
  - Per-run subdirectories with complete outputs

**Metrics Tracked**:
- Tour length (km)
- Travel time (hours)
- Waiting time (hours)
- Total work (Joules)
- Effective cost (Joules)
- Daylight penalty violations
- Runtime (seconds)

**Command**:
```bash
python experiment_runner.py
```

#### 2. Ant Count Optimization (`ants_optimization_experiment.py`)
**Purpose**: Determine optimal colony size

**Features**:
- Tests ant counts: [10, 20, 30, 40, 50, 75, 100]
- Multiple runs per ant count (default: 3)
- Records metrics at checkpoint iterations
- Identifies optimal balance between quality and runtime

**Outputs**:
- `ant_optimization_summary.csv` - Statistics per ant count
  - Average iterations to viable route
  - Standard deviations
  - Average/std runtimes
  - Cost metrics (best/worst/avg)
- `work_at_checkpoints.png` - Work progress comparison
- `iterations_to_viable.png` - Convergence speed vs ant count
- `runtime_vs_ants.png` - Computational cost scaling
- `efficiency_metric.png` - Combined efficiency metric
- `RECOMMENDATION.txt` - Optimal ant count with justification
- Per-run subdirectories with full algorithm outputs

**Command**:
```bash
python ants_optimization_experiment.py
```

#### 3. City Scaling Analysis (`city_scaling_experiment.py`)
**Purpose**: Understand how algorithm scales with problem size

**Features**:
- Tests problem sizes: [10, 15, 20, 25] cities
- Multiple runs per size (default: 5)
- Tracks iterations to first viable route
- Fits multiple mathematical models to data

**Models Fitted**:
- **Power Law**: $y = a \cdot x^b$ (polynomial scaling)
- **Exponential**: $y = a \cdot e^{bx}$ (exponential blowup)
- **Quadratic**: $y = a + bx + cx^2$ (polynomial)

**Outputs**:
- `city_scaling_summary.csv` - Per-size statistics
  - Viable runs count
  - Mean/std iterations to viable
  - Min/max iterations
- `scaling_analysis.png` - Main plot with all fitted curves
  - Shows data points with error bars
  - Compares model fits with R² values
  - Interpolates relationship for larger problems
- `convergence_curves_by_city_count.png` - Sample convergence curves
- `all_city_scaling_runs.csv` - Detailed per-run data
- `ANALYSIS.txt` - Complete fit results and interpretation
  - Model equations
  - R² goodness-of-fit
  - Big-O complexity analysis
  - Recommendations for scaling

**Command**:
```bash
python city_scaling_experiment.py
```

## Per-Run Outputs (All Experiments)

Each experiment run generates:

### Metric Tracking
- **`iteration_metrics.csv`** - Per-iteration convergence data
  - Iteration number
  - Best tour length (km)
  - Best travel time (hours)
  - Best waiting time (hours)
  - Best total work (Joules)
  - Best effective cost (Joules)
  - Daylight penalty status (Yes/No)
  - Epsilon (exploration rate)

### Visualizations
- **`convergence_length.png`** - Tour length convergence
- **`convergence_work.png`** - Work cost convergence
- **`convergence_travel_time.png`** - Travel time convergence
- **`triple_convergence.png`** - All metrics on one plot
- **`best_tour.png`** - Map of optimal route
- **`leg_velocities.png`** - Speed profile per leg
- **`leg_work.png`** - Work cost per leg
- **`pheromone_heatmap.png`** - Final pheromone distribution
- **`decision_heatmap.png`** - Ant exploration vs exploitation
- **`tour_animation.mp4`** - Route animation (if ffmpeg available)
- **`gantt_darkness_chart.png`** - Timeline with darkness windows
- **`population_coverage.png`** - Cumulative population delivered

### Data Exports
- **`final_best_tour.csv`** - Complete journey details
  - From/to cities
  - Distance, speed, travel time
  - Departure/arrival times (UTC and local)
  - Dark/light status
  - Work and effective costs
- **`final_route_coords.csv`** - Tour waypoints
  - City order
  - Coordinates for mapping
- **`pheromone_evolution/`** - Evolution of pheromone matrix
  - Snapshots at 10% interval checkpoints
  - Visualizes learning dynamics

## Configuration

### Main Algorithm Parameters

Edit in `main.py`:

```python
NUM_ITERATIONS = 6000           # Total optimization iterations
NUM_ANTS = 50                   # Colony size
NUM_CITIES = 41                 # Problem size

# ACO Parameters
ALPHA = 3                       # Pheromone influence
BETA = 2.1                      # Heuristic influence
RHO = 0.5                       # Evaporation rate
Q = 1.0                         # Deposit factor
TAU_MIN = 0.1                   # Min pheromone
TAU_MAX = 100.0                 # Max pheromone

# Exploration
INITIAL_EPSILON = 0.45          # Initial exploration rate
MIN_EPSILON = 0.05              # Minimum exploration
DECAY_RATE = 0.999962           # Decay per iteration

# Physics
DEFAULT_SANTA_SPEED_KMPH = 11500
AIR_DENSITY = 1.225             # kg/m³
```

### Experiment Parameters

Modify in respective experiment scripts:

```python
# experiment_runner.py
NUM_RUNS = 30

# ants_optimization_experiment.py
ANT_COUNTS = [10, 20, 30, 40, 50, 75, 100]
NUM_RUNS_PER_ANT_COUNT = 3

# city_scaling_experiment.py
CITY_COUNTS = [10, 15, 20, 25]
NUM_RUNS_PER_CITY_COUNT = 5
VIABLE_THRESHOLD = 1e14
```

## Output Directory Structure

```
~/Desktop/Dissertation Travelling Santa Problem/
├── main_run/                                # Main algorithm run
│   ├── iteration_metrics.csv
│   ├── final_best_tour.csv
│   ├── convergence_*.png
│   ├── pheromone_evolution/
│   └── ...
│
├── distance_only_baseline/                  # Distance-only baseline
│   ├── iteration_metrics_distance_only.csv
│   ├── best_tour_distance_only.csv
│   ├── convergence_distance_only.png
│   └── ...
│
├── multi_run_experiment/                    # 30-run validation (subdir per run)
│   ├── summary_statistics.csv               # Summary stats
│   ├── all_runs_metrics.csv                 # Detailed metrics
│   ├── metric_boxplots.png
│   ├── run_01/
│   │   ├── iteration_metrics.csv
│   │   ├── final_best_tour.csv
│   │   └── ...
│   ├── run_02/
│   └── ... (more runs)
│
├── ant_optimization/                        # Ant count testing
│   ├── ant_optimization_summary.csv         # Per-ant-count stats
│   ├── all_ant_runs.csv                     # Detailed per-run
│   ├── work_at_checkpoints.png
│   ├── iterations_to_viable.png
│   ├── runtime_vs_ants.png
│   ├── efficiency_metric.png
│   ├── RECOMMENDATION.txt                   # Optimal ant count
│   ├── ants_10_run_1/
│   ├── ants_20_run_1/
│   └── ... (more runs)
│
└── city_scaling/                            # City count scaling analysis
    ├── city_scaling_summary.csv             # Per-size stats
    ├── all_city_scaling_runs.csv            # Detailed per-run
    ├── scaling_analysis.png                 # Main plot with curve fits
    ├── convergence_curves_by_city_count.png
    ├── ANALYSIS.txt                         # Fit equations & complexity
    ├── cities_10_run_1/
    ├── cities_15_run_1/
    └── ... (more runs)
```

## Quick Start

### Single Run (Full Algorithm)
```bash
python main.py
# Output: ~/Desktop/Dissertation Travelling Santa Problem/main_run/
```

### Distance-Only Baseline
```bash
python distance_only_aco.py
# Output: ~/Desktop/Dissertation Travelling Santa Problem/distance_only_baseline/
```

### Statistical Validation (30 runs)
```bash
python experiment_runner.py
# Output: ~/Desktop/Dissertation Travelling Santa Problem/multi_run_experiment/
```

### Find Optimal Ant Count
```bash
python ants_optimization_experiment.py
# Output: ~/Desktop/Dissertation Travelling Santa Problem/ant_optimization/
# Key File: RECOMMENDATION.txt
```

### Analyze Scaling Behavior
```bash
python city_scaling_experiment.py
# Output: ~/Desktop/Dissertation Travelling Santa Problem/city_scaling/
# Key File: ANALYSIS.txt (with fitted equations and complexity)
```

## Key Metrics Explained

### Tour Length
Straight-line distance traveled (km). Lower is better.

### Travel Time
Actual flight time at varying speeds. Affected by acceleration/deceleration to meet darkness windows.

### Waiting Time
Time spent waiting at cities for darkness windows. High waiting time indicates poor scheduling.

### Work (Physical Cost)
Energy required to overcome air drag: $W = \frac{1}{2} \rho A v^2 \cdot d$
- $\rho$ = air density
- $A$ = dynamic cross-sectional area (varies with population coverage)
- $v$ = velocity
- $d$ = distance

### Effective Cost
Combines work cost with daylight penalties. The actual optimization objective.

$$\text{Effective Cost} = W \times f_{\text{darkness}} + P_{\text{penalty}}$$

Where:
- $f_{\text{darkness}}$ = 0.9 if arriving during darkness, 1.0 otherwise
- $P_{\text{penalty}}$ = huge penalty (10^100) if no valid darkness arrival

## Research Applications

### 1. Validating Algorithm Robustness
**experiment_runner.py** shows if results are stable across runs or high-variance.

### 2. Tuning Colony Size
**ants_optimization_experiment.py** identifies the sweet spot between solution quality and computational cost.

### 3. Predicting Scalability
**city_scaling_experiment.py** allows extrapolation:
- If power law with $b=2$: O(n²) complexity
- If exponential: Intractable for large n
- Can predict feasibility for larger problems

### 4. Baseline Comparison
**distance_only_aco.py** quantifies the overhead of adding realistic constraints (darkness, work, time).

## Dependencies

```
numpy
matplotlib
scipy
```

Install via:
```bash
pip install numpy matplotlib scipy
```

## Notes

- All timestamps use UTC internally with timezone conversions for darkness checks
- Darkness windows use fixed date: Dec 24 (sunset) to Dec 25 (sunrise)
- North Pole has special handling (always dark)
- Speed is dynamically adjusted to meet darkness arrival windows
- Pheromone matrix uses both forward and reverse edges

## Citation

If using this code for research, cite as:

```
Travelling Santa Problem - ACO Experiment Suite
Physics-informed Ant Colony Optimization for constrained routing
[Author, Institution, Year]
```

## License

[Your License Here]

---

**Last Updated**: February 2026  
**Framework Version**: 1.0
