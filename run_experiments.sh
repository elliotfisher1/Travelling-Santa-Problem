#!/bin/bash
# Travelling Santa Problem - Experiment Runner Script
# Run all experiments in sequence with proper logging

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$HOME/Desktop/Dissertation Travelling Santa - Experiment Logs"
mkdir -p "$LOG_DIR"

echo "=========================================="
echo "Travelling Santa Problem - Experiment Suite"
echo "=========================================="
echo "Logging to: $LOG_DIR"
echo ""

# Function to run experiment with timing
run_experiment() {
    local name=$1
    local script=$2
    local log_file="$LOG_DIR/${name}_$(date +%Y%m%d_%H%M%S).log"
    
    echo "Starting: $name"
    echo "Log file: $log_file"
    echo "---"
    
    start_time=$(date +%s)
    
    if python "$SCRIPT_DIR/$script" 2>&1 | tee "$log_file"; then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo "✓ $name completed successfully in $duration seconds"
    else
        echo "✗ $name failed. Check log: $log_file"
        return 1
    fi
    echo ""
}

# Parse arguments
EXPERIMENTS="all"
if [ $# -gt 0 ]; then
    EXPERIMENTS=$1
fi

# Run experiments
case $EXPERIMENTS in
    all)
        echo "Running ALL experiments..."
        run_experiment "Distance Only Baseline" "distance_only_aco.py"
        run_experiment "Multi-Run Validation" "experiment_runner.py"
        run_experiment "Ant Count Optimization" "ants_optimization_experiment.py"
        run_experiment "City Scaling Analysis" "city_scaling_experiment.py"
        ;;
    baseline)
        run_experiment "Distance Only Baseline" "distance_only_aco.py"
        ;;
    multirun)
        run_experiment "Multi-Run Validation" "experiment_runner.py"
        ;;
    ants)
        run_experiment "Ant Count Optimization" "ants_optimization_experiment.py"
        ;;
    scaling)
        run_experiment "City Scaling Analysis" "city_scaling_experiment.py"
        ;;
    *)
        echo "Usage: $0 [all|baseline|multirun|ants|scaling]"
        echo ""
        echo "  all       - Run all experiments (warning: very long!)"
        echo "  baseline  - Run distance-only baseline only"
        echo "  multirun  - Run 30-run validation only"
        echo "  ants      - Run ant count optimization only"
        echo "  scaling   - Run city scaling analysis only"
        exit 1
        ;;
esac

echo "=========================================="
echo "Experiment suite complete!"
echo "Check logs in: $LOG_DIR"
echo "=========================================="
