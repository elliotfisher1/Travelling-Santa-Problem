# The Travelling Santa Problem

Every Christmas Eve, Santa Claus must deliver gifts to cities across the world - but with one critical constraint: he can only travel in darkness. Arriving at a city while the sun is up risks being seen, so his route must be carefully timed to exploit the progression of night across time zones.

This project frames that scenario as an optimisation problem and solves it using Ant Colony Optimisation (ACO) - an algorithm inspired by how real ant colonies find efficient paths through pheromone trails. Rather than simply finding the shortest route, the algorithm must balance tour distance, physical energy expenditure, and the hard constraint of arriving at every city under the cover of night.

---

## The Problem

The classic Travelling Salesman Problem asks: given a list of cities, what is the shortest possible route that visits each city exactly once and returns to the start?

The Travelling Santa Problem adds real-world complexity:

- **Darkness constraint** - Santa may only arrive at a city during its local night window (between sunset and sunrise). Violating this incurs a massive penalty.
- **Physics-based cost** - the route is not just evaluated on distance. The algorithm models the aerodynamic work required to fly the sleigh, accounting for air drag, speed, and the cumulative energy of the full journey.
- **Time zones and scheduling** - each city has a real geographic location, timezone offset, and local sunrise/sunset times for December 24th. The clock advances as Santa travels, making sequencing critical.

The goal is to find a route that visits all cities, respects every city's darkness window, and minimises the total physical work done - not just the kilometres flown.

---

## How It Works

### Ant Colony Optimisation

ACO is a nature-inspired metaheuristic. A colony of artificial "ants" each constructs a candidate route through the cities. After each round, routes that performed well deposit virtual pheromone on the edges they used. Over thousands of iterations, the colony converges on an increasingly efficient path - with worse routes fading as their pheromone evaporates.

Key parameters that shape the search:

| Parameter | Role |
|-----------|------|
| `ALPHA` | How strongly ants follow existing pheromone trails |
| `BETA` | How strongly ants prefer shorter/cheaper edges |
| `RHO` | Rate at which pheromone evaporates each iteration |
| `EPSILON` | Probability of random exploration (decays over time) |

The algorithm starts with high exploration (ants take more random paths) and gradually shifts toward exploitation (ants reinforce the best routes found so far).

### The Cost Function

At each candidate route, the algorithm calculates:
1. **Total tour length** - the sum of great-circle distances between cities
2. **Total work** - aerodynamic energy cost of the full journey
3. **Darkness penalty** - an enormous penalty (`2.1 × 10¹⁰⁰`) applied whenever Santa arrives at a city in daylight

This penalty is so severe that the algorithm effectively treats a daylight violation as an invalid solution, forcing the colony to find routes that respect all time windows before optimising further.

---

## Cities

The problem covers major world cities spanning every continent and time zone, including Tokyo, Delhi, Cairo, London, New York, São Paulo, and Sydney. Each city carries its real coordinates, population, timezone, and December 24th sunrise/sunset times.

The December 24th date is deliberate - not only is it Christmas Eve, but it also sets the specific daylight windows Santa must navigate, with shorter days in the northern hemisphere winter and longer days in the south.

---

## Files

### Core Algorithm

**`main.py`** - The full Travelling Santa Problem solver. Runs 60,000 iterations with 14 ants, enforces darkness constraints, and outputs convergence data, route maps, pheromone evolution snapshots, a Gantt chart showing each city's darkness window, and an animated tour.

**`distance_only_aco.py`** - A stripped-back baseline that solves the same city set but ignores all constraints, optimising only for shortest distance. Used to quantify how much the darkness and physics constraints change the resulting route and convergence behaviour.

### Experiments

**`ants_optimization_experiment.py`** - Tests colony sizes of 5, 10, 25, 50, and 75 ants across multiple runs to find the optimal number. Outputs recommendation on which ant count best balances solution quality against runtime.

**`city_scaling_experiment.py`** - Progressively increases the number of cities (10 → 25) and fits mathematical models (power law, exponential, quadratic) to the results. Reveals the computational complexity of the problem and predicts how it would scale to larger city sets.

**`convergence_with_error_bars.py`** - Runs the algorithm multiple times and plots convergence curves with error bars, showing how consistent the colony is at finding good solutions and where variance is highest.

**`full_scale_convergence_experiment.py`** - A comprehensive convergence analysis over the full city set, tracking how solution quality evolves across the entire run.

**`experiment_runner.py`** - Orchestrates all experiments in sequence, collecting results and generating summary statistics across 30 runs.

### Utilities

**`plots.py`** - Generates dual-axis convergence plots comparing the constrained TSaP against the distance-only baseline, showing both tour length and work on the same chart.

**`generate_summary.py`** - Aggregates results across experiment runs into a single summary report.

**`run_experiments.sh`** - Shell script to run all experiments from the command line in one go.

**`INDEX.py`** - An index of all scripts and their functions for quick navigation.

---

## Key Outputs

- **Convergence plots** - how tour length and work improve over iterations
- **Route maps** - geographic visualisation of the best tour found
- **Gantt chart** - each city's darkness window against Santa's arrival time
- **Pheromone heatmaps** - how the colony's confidence in each route edge builds over time
- **Tour animation** - animated playback of Santa's optimal route
- **Statistical summaries** - mean, standard deviation, best and worst across repeated runs

---

## Context

This project was developed as part of a dissertation exploring physics-informed optimisation. The central argument is that adding real-world constraints (time windows, energy cost) to a classical TSP not only changes the optimal route but meaningfully changes the shape of the search - which the experiments are designed to demonstrate through comparison with the unconstrained baseline.
