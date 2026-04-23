#!/usr/bin/env python3
"""
Travelling Santa Problem - Complete Research Framework
Master Index and Quick Reference

This file serves as the main entry point for understanding the entire project.
"""

# ==============================================================================
# PROJECT STRUCTURE
# ==============================================================================

"""
Travelling-Santa-Problem-1/
├── README.md                           # Original project overview
├── EXPERIMENT_GUIDE.md                 # Comprehensive experiment guide ⭐ START HERE
├── IMPLEMENTATION_SUMMARY.md           # Technical implementation details
├── main.py                             # Full TSP algorithm (MODIFIED)
├── distance_only_aco.py                # Baseline: distance-only ACO
├── experiment_runner.py                # Multi-run statistical validation (30 runs)
├── ants_optimization_experiment.py     # Ant count optimization (10,20,30,40,50,75,100)
├── city_scaling_experiment.py          # Scaling analysis (10,15,20,25 cities)
└── run_experiments.sh                  # Orchestration script for all experiments
"""

# ==============================================================================
# QUICK START
# ==============================================================================

"""
1. READ FIRST:
   - EXPERIMENT_GUIDE.md (comprehensive overview)
   - IMPLEMENTATION_SUMMARY.md (technical details)

2. RUN A SINGLE EXAMPLE:
   python main.py
   # Output: ~/Desktop/Dissertation Travelling Santa Problem 50/

3. RUN ALL EXPERIMENTS:
   bash run_experiments.sh all
   # Takes 10-15 hours - run overnight!

4. OR RUN INDIVIDUAL EXPERIMENTS:
   python distance_only_aco.py          # 5 min - baseline comparison
   python experiment_runner.py          # 3-5 hours - statistical validation
   python ants_optimization_experiment.py     # 2-3 hours - ant count tuning
   python city_scaling_experiment.py    # 2-3 hours - scaling analysis
"""

# ==============================================================================
# WHAT EACH FILE DOES
# ==============================================================================

FILES = {
    "main.py": {
        "Type": "Core Algorithm",
        "Purpose": "Full TSP algorithm with darkness constraints",
        "Modifications": "Added per-iteration CSV logging",
        "Output": "iteration_metrics.csv + visualizations",
        "Time": "5-10 min per run",
        "Key Metrics": [
            "Tour length (km)",
            "Travel time (hours)",
            "Work cost (Joules)",
            "Effective cost (Joules)",
            "Daylight penalties"
        ]
    },
    
    "distance_only_aco.py": {
        "Type": "Baseline Implementation",
        "Purpose": "Distance-minimization only (no constraints)",
        "Use Case": "Compare full algorithm overhead vs simpler variant",
        "Output": "iteration_metrics_distance_only.csv",
        "Time": "5 min",
        "Creates": "Baseline for algorithm comparison"
    },
    
    "experiment_runner.py": {
        "Type": "Multi-Run Experiment",
        "Purpose": "Statistical validation across 30 runs",
        "What It Tests": "Algorithm robustness and consistency",
        "Outputs": [
            "summary_statistics.csv (mean/std/best/worst)",
            "metric_boxplots.png (4-panel distribution visualization)",
            "all_runs_metrics.csv (detailed per-run data)",
            "30 run subdirectories with full outputs"
        ],
        "Time": "3-5 hours",
        "Success Metric": "Low std dev = robust algorithm"
    },
    
    "ants_optimization_experiment.py": {
        "Type": "Parameter Tuning Experiment",
        "Purpose": "Find optimal colony size",
        "Tests": "Ant counts [10, 20, 30, 40, 50, 75, 100]",
        "Outputs": [
            "ant_optimization_summary.csv (per-ant-count statistics)",
            "work_at_checkpoints.png (convergence comparison)",
            "iterations_to_viable.png (convergence speed)",
            "runtime_vs_ants.png (computational cost)",
            "efficiency_metric.png (combined score)",
            "RECOMMENDATION.txt (optimal ant count)"
        ],
        "Time": "2-3 hours",
        "Key Finding": "Identifies sweet spot between quality and runtime"
    },
    
    "city_scaling_experiment.py": {
        "Type": "Scaling Analysis Experiment",
        "Purpose": "Understand how algorithm scales with problem size",
        "Tests": "Problem sizes [10, 15, 20, 25] cities",
        "Outputs": [
            "city_scaling_summary.csv (per-size statistics)",
            "scaling_analysis.png (data + fitted curves)",
            "convergence_curves_by_city_count.png (sample runs)",
            "ANALYSIS.txt (fitted equations + complexity analysis)"
        ],
        "Time": "2-3 hours",
        "Models Fitted": [
            "Power Law: y = a*x^b (polynomial scaling)",
            "Exponential: y = a*exp(b*x) (exponential blowup)",
            "Quadratic: y = a + bx + cx^2 (polynomial)"
        ],
        "Key Finding": "Complexity classification + extrapolation potential"
    },
    
    "run_experiments.sh": {
        "Type": "Orchestration Script",
        "Purpose": "Run experiments with logging and timing",
        "Usage": [
            "bash run_experiments.sh all      # All experiments",
            "bash run_experiments.sh baseline # Distance-only",
            "bash run_experiments.sh multirun # 30-run validation",
            "bash run_experiments.sh ants     # Ant optimization",
            "bash run_experiments.sh scaling  # City scaling"
        ]
    },
    
    "EXPERIMENT_GUIDE.md": {
        "Type": "Documentation",
        "Purpose": "Comprehensive guide to all experiments",
        "Contents": [
            "Project overview",
            "File descriptions",
            "Configuration parameters",
            "Output structure",
            "Metric explanations",
            "Research applications",
            "Quick start guide"
        ],
        "Read This For": "Understanding what each experiment does and why"
    },
    
    "IMPLEMENTATION_SUMMARY.md": {
        "Type": "Technical Documentation",
        "Purpose": "Implementation details and design decisions",
        "Contents": [
            "Changes to main.py",
            "New file descriptions",
            "Data flow and dependencies",
            "Design decisions",
            "Computational costs",
            "Verification checklist"
        ],
        "Read This For": "How things are implemented and future extensions"
    }
}

# ==============================================================================
# EXPERIMENTAL FLOW
# ==============================================================================

EXPERIMENTAL_FLOW = """
START
  ↓
(1) RUN SINGLE EXAMPLE: python main.py
    └─→ Outputs: Single run with visualizations
  ↓
(2) ESTABLISH BASELINE: python distance_only_aco.py
    └─→ Outputs: Distance-only solution for comparison
  ↓
(3) VALIDATE ROBUSTNESS: python experiment_runner.py
    └─→ Outputs: 30 runs, statistics, boxplots
    └─→ Question: Is the algorithm stable across runs?
  ↓
(4) OPTIMIZE PARAMETERS: python ants_optimization_experiment.py
    └─→ Outputs: Optimal ant count with recommendation
    └─→ Question: What's the best balance of quality vs runtime?
  ↓
(5) ANALYZE SCALING: python city_scaling_experiment.py
    └─→ Outputs: Fitted models for problem size scaling
    └─→ Question: How does performance change with problem size?
  ↓
END: Publish/document results
"""

# ==============================================================================
# TYPICAL EXPERIMENT SEQUENCE
# ==============================================================================

EXPERIMENT_SEQUENCE = """
For a research paper, follow this workflow:

1. INITIAL VALIDATION (30 min)
   - Run main.py once to verify setup
   - Run distance_only_aco.py for baseline
   - Check output directories created successfully

2. ROBUSTNESS TESTING (3-5 hours)
   - Run experiment_runner.py (30 runs)
   - Analyze summary_statistics.csv
   - Create Publication Figure 1: boxplots

3. PARAMETER OPTIMIZATION (2-3 hours)
   - Run ants_optimization_experiment.py
   - Review RECOMMENDATION.txt
   - Create Publication Figure 2: efficiency curves

4. SCALABILITY ANALYSIS (2-3 hours)
   - Run city_scaling_experiment.py
   - Review ANALYSIS.txt (fitted equations)
   - Create Publication Figure 3: scaling curves with fits

5. FINAL ANALYSIS (1-2 hours)
   - Aggregate results across all experiments
   - Write paper/thesis chapter
   - Include CSVs as supplementary data
"""

# ==============================================================================
# KEY RESULTS BY EXPERIMENT
# ==============================================================================

EXPECTED_OUTPUTS = {
    "experiment_runner.py": [
        "Summary statistics (mean ± std) for all metrics",
        "Boxplots showing distributions",
        "Success rate (% runs without daylight penalties)",
        "Variance in tour length and cost across runs"
    ],
    
    "ants_optimization_experiment.py": [
        "Optimal ant count recommendation",
        "Convergence speed vs colony size",
        "Runtime scaling with ant count",
        "Efficiency (quality per second) metric"
    ],
    
    "city_scaling_experiment.py": [
        "Fitted power law: y = a*x^b",
        "Fitted exponential: y = a*exp(b*x)",
        "R² values for model comparison",
        "Big-O complexity classification",
        "Extrapolation capability to larger problems"
    ]
}

# ==============================================================================
# DIRECTORY STRUCTURE OF OUTPUTS
# ==============================================================================

OUTPUT_STRUCTURE = """
~/Desktop/Dissertation Travelling Santa Problem - [Experiment Type]/
├── iteration_metrics.csv                 # Per-iteration tracking (KEY)
├── summary_statistics.csv                # Summary stats (for multi-run)
├── all_runs_metrics.csv                  # Detailed per-run data
├── RECOMMENDATION.txt                    # (for ant optimization)
├── ANALYSIS.txt                          # (for city scaling)
├── *.png                                 # Visualization plots
├── pheromone_evolution/                  # Pheromone snapshots
└── run_01/, run_02/, ..., run_XX/        # Individual run directories
    ├── iteration_metrics.csv
    ├── final_best_tour.csv
    ├── final_route_coords.csv
    ├── convergence_*.png
    ├── best_tour.png
    ├── gantt_darkness_chart.png
    └── population_coverage.png
"""

# ==============================================================================
# QUICK REFERENCE: RUNNING EXPERIMENTS
# ==============================================================================

QUICK_COMMANDS = """
# Single run with full output
python main.py

# Baseline for comparison
python distance_only_aco.py

# Statistical validation (30 runs)
python experiment_runner.py

# Find optimal ant count
python ants_optimization_experiment.py

# Analyze scaling behavior
python city_scaling_experiment.py

# Run everything (takes 10-15 hours)
bash run_experiments.sh all

# Run specific experiment
bash run_experiments.sh scaling
bash run_experiments.sh ants
bash run_experiments.sh multirun
bash run_experiments.sh baseline
"""

# ==============================================================================
# TROUBLESHOOTING
# ==============================================================================

TROUBLESHOOTING = """
Problem: "Module not found" error
Solution: Install dependencies
  pip install numpy matplotlib scipy

Problem: "Permission denied" on shell script
Solution: Make executable
  chmod +x run_experiments.sh

Problem: Disk space full
Solution: Clear intermediate outputs or use smaller problem sizes
  - Modify CITY_COUNTS = [10, 15] in city_scaling_experiment.py
  - Reduce NUM_RUNS in experiment_runner.py

Problem: Experiment taking too long
Solution: Reduce iterations or runs
  - Modify NUM_ITERATIONS in main.py (default 6000)
  - Reduce NUM_RUNS in experiment_runner.py (default 30)
  
Problem: CSV not updating
Solution: Check MAIN_OUTPUT_DIR path
  - Verify ~/Desktop/Dissertation... directories exist
  - Check write permissions
"""

# ==============================================================================
# CITATION AND REFERENCE
# ==============================================================================

CITATION = """
If using this framework in research, please cite:

@misc{travelingsanta-aco,
  title={Travelling Santa Problem: ACO Research Framework},
  author={Your Name},
  year={2026},
  howpublished={\\url{https://github.com/...}}
}

Key publications to reference:
- Dorigo & Stützle (2004): Ant Colony Optimization
- Solomon (1987): VRPTW benchmark problems
- [Your paper]: TSP with darkness constraints
"""

# ==============================================================================
# MAIN ENTRY POINT
# ==============================================================================

if __name__ == "__main__":
    import os
    
    print("=" * 80)
    print("TRAVELLING SANTA PROBLEM - ACO RESEARCH FRAMEWORK")
    print("=" * 80)
    print()
    print("📚 DOCUMENTATION:")
    print("   1. Read EXPERIMENT_GUIDE.md for overview")
    print("   2. Read IMPLEMENTATION_SUMMARY.md for technical details")
    print()
    print("🚀 QUICK START:")
    print("   python main.py                          # Single run")
    print("   python distance_only_aco.py             # Baseline")
    print("   python experiment_runner.py             # 30-run validation")
    print("   python ants_optimization_experiment.py  # Ant tuning")
    print("   python city_scaling_experiment.py       # Scaling analysis")
    print("   bash run_experiments.sh all             # All experiments")
    print()
    print("📊 OUTPUT LOCATIONS:")
    print("   ~/Desktop/Dissertation Travelling Santa Problem - [Type]/")
    print()
    print("❓ FOR HELP:")
    print("   See EXPERIMENT_GUIDE.md section 'Quick Start'")
    print("=" * 80)
