# Guide

This document covers everything you need to run the Travelling Santa Problem experiments: setup, configuration, what the metrics mean, where outputs are saved, and what to do when things go wrong.

---

## Setup

### Dependencies

```bash
pip install numpy matplotlib scipy
```

Python 3.7 or above is required.

### Disk space

A single run produces around 500 MB of output (convergence plots, pheromone snapshots, animations). The full experiment suite across all runs needs 20–50 GB. Check you have space before starting:

```bash
df -h $HOME
```

---

## Running the experiments

### Start here: single run

```bash
python main.py
```

This runs the full Travelling Santa Problem - 60,000 iterations, 14 ants, darkness constraints enforced. A good first step to confirm everything is working before committing to longer experiment runs. Takes roughly 5–10 minutes.

### Baseline comparison

```bash
python distance_only_aco.py
```

Runs the same city set but ignores all constraints - no darkness windows, no physics cost, just shortest distance. Use this to compare against the full algorithm and quantify how much the constraints change the route and convergence behaviour.

### Statistical validation

```bash
python experiment_runner.py
```

Runs the full algorithm 30 times and aggregates the results. Produces mean, standard deviation, best, and worst values for each metric, plus boxplots of the distributions. Takes 3–5 hours. Best run overnight.

### Ant count optimisation

```bash
python ants_optimization_experiment.py
```

Tests colony sizes of 5, 10, 25, 50, and 75 ants across 3 runs each. Outputs a `RECOMMENDATION.txt` identifying the colony size that best balances solution quality against runtime. Takes 2–3 hours.

### City scaling analysis

```bash
python city_scaling_experiment.py
```

Progressively increases the number of cities from 10 to 25 and fits power law, exponential, and quadratic models to the results. Outputs an `ANALYSIS.txt` with the fitted equations, R² values, and a Big-O complexity estimate. Takes 2–3 hours.

### Run everything

```bash
bash run_experiments.sh all
```

Runs all experiments sequentially. Budget 10–15 hours and leave it running.

---

## Configuration

All key parameters are set at the top of each script.

### Main algorithm (`main.py`)

```python
NUM_ITERATIONS = 60000   # Total optimisation iterations
NUM_ANTS = 14            # Colony size

ALPHA = 3                # How strongly ants follow pheromone trails
BETA = 2.1               # How strongly ants prefer shorter/cheaper edges
RHO = 0.5                # Pheromone evaporation rate per iteration
TAU_MIN = 0.1            # Minimum pheromone level
TAU_MAX = 100.0          # Maximum pheromone level

INITIAL_EPSILON = 0.45   # Starting exploration rate
MIN_EPSILON = 0.05       # Minimum exploration rate (floor)
DECAY_RATE = 0.99996638  # How quickly exploration decays toward exploitation
```

### Experiments

```python
# experiment_runner.py
NUM_RUNS = 30

# ants_optimization_experiment.py
ANT_COUNTS = [5, 10, 25, 50, 75]
NUM_RUNS_PER_ANT_COUNT = 3

# city_scaling_experiment.py
CITY_COUNTS = [10, 15, 20, 25]
NUM_RUNS_PER_CITY_COUNT = 5
```

---

## Understanding the metrics

Each run tracks the following per iteration, saved to `iteration_metrics.csv`:

**Tour length (km)** - the total great-circle distance of the route. Lower is better, but this is not the primary optimisation target.

**Travel time (hours)** - actual flight time at the speeds Santa flies each leg. This varies because speed is dynamically adjusted to hit darkness windows.

**Waiting time (hours)** - time spent at cities waiting for night to fall. High waiting time means the route ordering is inefficient; Santa is arriving somewhere too early and sitting idle.

**Total work (Joules)** - the physical energy cost of the journey, modelled as aerodynamic drag: W = ½ρAv²d, where ρ is air density, A is the sleigh's cross-sectional area, v is speed, and d is distance. This is the primary quantity the algorithm is trying to minimise.

**Effective cost (Joules)** - the actual value being optimised. Combines total work with the darkness penalty:

- If Santa arrives at every city in darkness: effective cost ≈ total work × 0.9 (a small bonus)
- If any city is visited in daylight: effective cost += 2.1 × 10¹⁰⁰ (effectively infinite)

**Daylight penalty** - whether the current best route violates any darkness window. Once the algorithm finds its first fully valid route (no daylight arrivals), this flips off and stays off.

**Epsilon** - the current exploration rate. Starts at 0.45 and decays toward 0.05 over the run. High epsilon means ants are exploring new paths; low epsilon means they are reinforcing known good routes.

---

## Outputs

All outputs are saved under:

```
~/Desktop/Travelling Santa Problem/
├── main_run/
├── distance_only_baseline/
├── multi_run_experiment/
├── ant_optimization/
└── city_scaling/
```

### Per run

Every run (including those inside experiments) produces:

| File | Contents |
|------|----------|
| `iteration_metrics.csv` | One row per iteration: all metrics above |
| `final_best_tour.csv` | Complete journey - each leg's distance, speed, departure/arrival times, dark/light status, work cost |
| `final_route_coords.csv` | City order and coordinates for mapping |
| `convergence_length.png` | Tour length over iterations |
| `convergence_work.png` | Work cost over iterations |
| `convergence_travel_time.png` | Travel time over iterations |
| `best_tour.png` | Map of the best route found |
| `gantt_darkness_chart.png` | Timeline showing each city's darkness window and Santa's arrival |
| `pheromone_heatmap.png` | Final pheromone distribution across all city pairs |
| `decision_heatmap.png` | Where ants explored vs exploited |
| `tour_animation.mp4` | Animated playback of the route (requires ffmpeg) |
| `pheromone_evolution/` | Pheromone matrix snapshots at 10% iteration intervals |

### Experiment summaries

| Experiment | Key output file |
|------------|----------------|
| Multi-run (`experiment_runner.py`) | `summary_statistics.txt` - mean ± std across 30 runs |
| Ant optimisation | `RECOMMENDATION.txt` - optimal colony size with justification |
| City scaling | `ANALYSIS.txt` - fitted equations, R² values, complexity classification |

---
CSVs are written per-iteration and flushed to disk, so partial data is recoverable. Re-run the specific experiment; completed run subdirectories will already exist.

