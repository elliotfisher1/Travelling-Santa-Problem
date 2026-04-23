## Repository contents (updated)

The following files are present in the project's root directory:

```
00_START_HERE.md
ACO_TSP_PROCEDURE.md
COMPLETION_SUMMARY.md
DIRECTORY_STRUCTURE.md
EXECUTION_CHECKLIST.md
EXPERIMENT_GUIDE.md
IMPLEMENTATION_SUMMARY.md
INDEX.py
main.py
ants_optimization_experiment.py
city_scaling_experiment.py
convergence_with_error_bars.py
distance_only_aco.py
experiment_runner.py
full_scale_convergence_experiment.py
generate_summary.py
plots.py
run_experiments.sh
```

Note: `__pycache__/` and `.DS_Store` are generated and can be ignored.

### Experiments

- **ants_optimization_experiment.py**: Implements the Ant Colony Optimization algorithm for solving the Traveling Salesman Problem and outputs the best route found.
- **city_scaling_experiment.py**: Tests the routing algorithm on cities of varying sizes to benchmarks performance metrics.
- **convergence_with_error_bars.py**: Convergence analysis of the algorithm including error bars to visualize the variability in output over multiple runs.
- **distance_only_aco.py**: Conducts experiments focusing solely on distance optimization without other parameters.
- **full_scale_convergence_experiment.py**: Comprehensive convergence analysis over a full-scale problem instance, assessing performance across iterations.

### Utilities

- **plots.py**: Contains functions for generating and saving visualization plots based on experiment results.
- **generate_summary.py**: Aggregates experiment results and generates a summary report for easier interpretation of data.
- **INDEX.py**: Provides an overview and index of available scripts and functions within the repository.
- **experiment_runner.py**: A utility that orchestrates the execution of all experiment scripts.
- **run_experiments.sh**: A shell script designed to run all experiments in sequence.
