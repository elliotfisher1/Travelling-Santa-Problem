# Travelling Santa Problem (ACO)  
Ant Colony Optimisation (ACO) solution to a “Travelling Santa” variant of the TSP, where Santa must visit each city during local darkness (night-time delivery constraint). The objective is to find a feasible global tour while balancing distance, travel time, waiting time, and a work/energy cost model.

This repository contains a single Python script that:
- Builds a world tour over a fixed list of cities (lat/lon + timezone + sunrise/sunset + population)
- Uses ACO with pheromone update rules and epsilon-greedy exploration
- Enforces darkness windows (with configurable sunrise/sunset buffers)
- Produces extensive CSV + visual outputs (convergence curves, heatmaps, Gantt chart, tour plot, animation, etc.)

---

## Key idea
Classic TSP is “shortest route visiting each city once.”  
This project adds a real-world constraint: Santa should arrive during the city’s darkness window.

A large penalty is applied to routes that break the darkness constraint (configurable).

---

## Features
- **Ant Colony Optimisation (ACO)**:
  - Pheromone influence (`ALPHA`)
  - Heuristic influence (`BETA`) based on *effective cost*
  - Evaporation (`RHO`) that decreases over time
  - Global best reinforcement
  - Pheromone clamping (`TAU_MIN`, `TAU_MAX`)
- **Exploration vs exploitation**:
  - Epsilon-greedy (`EPSILON`) decays each iteration
  - Decision history stored per ant and visualised
- **Darkness constraint**:
  - Uses city sunrise/sunset with buffers
  - Converts between UTC and local time using `tz_offset`
- **Physics-inspired cost**:
  - “Work” approximated via drag-style model:  
    `0.5 * rho_air * area * v^2 * distance`
  - Dynamic cross-sectional area shrinks as population coverage increases
- **Outputs**:
  - Per-iteration “milestone” folders with plots + CSVs
  - Pheromone evolution heatmaps
  - Final best tour and route coordinates

---

## Project structure
```text
.
├── Main.py              # Main script 
└── README.md
