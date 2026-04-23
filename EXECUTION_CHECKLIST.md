# Travelling Santa Problem - Experiment Execution Checklist

## Pre-Experiment Setup ✓

### Environment Verification
- [ ] Python 3.7+ installed
  ```bash
  python --version
  ```
- [ ] Required packages installed
  ```bash
  pip install numpy matplotlib scipy
  ```
- [ ] Disk space check (50+ GB recommended)
  ```bash
  df -h $HOME
  ```
- [ ] All .py files in correct directory
  ```bash
  ls -la /Users/elliotfisher/Travelling-Santa-Problem-1/*.py
  ```

### Documentation Review
- [ ] Read EXPERIMENT_GUIDE.md
- [ ] Reviewed IMPLEMENTATION_SUMMARY.md
- [ ] Understood expected outputs

---

## Experiment 1: Single Run (Validation)

**Estimated Time**: 5-10 minutes  
**Purpose**: Verify setup works correctly

### Execution
```bash
cd /Users/elliotfisher/Travelling-Santa-Problem-1
python main.py
```

### Verification Checklist
- [ ] No errors in terminal
- [ ] Output directory created: `~/Desktop/Dissertation Travelling Santa Problem 50/`
- [ ] Check for key files:
  - [ ] `iteration_metrics.csv` exists and has data
  - [ ] `final_best_tour.csv` exists
  - [ ] PNG files generated (convergence plots, tour map, etc.)
- [ ] CSV file has 6000 rows (one per iteration)
- [ ] Metrics make sense:
  - [ ] Tour length in range 50,000-200,000 km
  - [ ] Travel time < 1000 hours
  - [ ] Work cost > 0

**Next Step**: If verification passes, proceed to Baseline experiment.

---

## Experiment 2: Baseline (Distance-Only ACO)

**Estimated Time**: 5-10 minutes  
**Purpose**: Create baseline for comparison

### Execution
```bash
python distance_only_aco.py
```

### Verification Checklist
- [ ] No errors in terminal
- [ ] Output directory created: `~/Desktop/Dissertation Travelling Santa Problem - Distance Only Baseline/`
- [ ] Files created:
  - [ ] `iteration_metrics_distance_only.csv`
  - [ ] `best_tour_distance_only.csv`
  - [ ] `convergence_distance_only.png`
- [ ] Tour length is shorter than full algorithm (expected)

**Comparison**:
```bash
# Compare metrics
tail -1 "~/Desktop/Dissertation Travelling Santa Problem 50/iteration_metrics.csv"
tail -1 "~/Desktop/Dissertation Travelling Santa Problem - Distance Only Baseline/iteration_metrics_distance_only.csv"
```

**Next Step**: If baseline complete, proceed to multi-run validation.

---

## Experiment 3: Multi-Run Validation

**Estimated Time**: 3-5 hours  
**Purpose**: Statistical validation across 30 runs

### Pre-Execution
- [ ] Clear schedule (3-5 hours uninterrupted)
- [ ] Close other resource-intensive applications
- [ ] Monitor disk space (needs 20+ GB)

### Execution
```bash
python experiment_runner.py
```

### Real-Time Monitoring
```bash
# In another terminal, monitor progress
watch -n 60 'ls -d ~/Desktop/Dissertation\ Travelling\ Santa\ -\ Multi-Run\ Experiment/run_* | wc -l'
```

### Verification Checklist (During)
- [ ] Run subdirectories being created (run_01/, run_02/, etc.)
- [ ] Runs completing sequentially
- [ ] No error messages

### Verification Checklist (After)
- [ ] 30 run directories created
- [ ] Output directory structure:
  - [ ] `summary_statistics.csv` exists
  - [ ] `summary_statistics.txt` exists (human-readable)
  - [ ] `metric_boxplots.png` exists
  - [ ] `all_runs_metrics.csv` exists
- [ ] Statistics file contains:
  - [ ] Mean ± Std Dev for each metric
  - [ ] Best/Worst values
  - [ ] Success rate information

### Analysis
```bash
# View summary statistics
cat "~/Desktop/Dissertation Travelling Santa - Multi-Run Experiment/summary_statistics.txt"

# Check success rate (% runs without penalties)
grep "Success rate" "~/Desktop/Dissertation Travelling Santa - Multi-Run Experiment/summary_statistics.txt"
```

**Interpretation**:
- Low std dev → Algorithm is robust ✓
- High std dev → Results vary significantly
- High success rate → Constraints easily satisfied
- Low success rate → Problem is challenging

**Next Step**: If statistics look reasonable, proceed to ant optimization.

---

## Experiment 4: Ant Count Optimization

**Estimated Time**: 2-3 hours  
**Purpose**: Find optimal colony size

### Pre-Execution
- [ ] Clear schedule (2-3 hours uninterrupted)
- [ ] Needs ~15 GB disk space

### Execution
```bash
python ants_optimization_experiment.py
```

### Real-Time Monitoring
```bash
# Monitor runs
ls ~/Desktop/Dissertation\ Travelling\ Santa\ -\ Ant\ Optimization/ | wc -l
```

### Verification Checklist (After)
- [ ] Output directory created
- [ ] Subdirectories for each ant count (ants_10_run_1, ants_20_run_1, etc.)
- [ ] Key output files:
  - [ ] `ant_optimization_summary.csv`
  - [ ] `all_ant_runs.csv`
  - [ ] `RECOMMENDATION.txt`
  - [ ] `work_at_checkpoints.png`
  - [ ] `iterations_to_viable.png`
  - [ ] `runtime_vs_ants.png`
  - [ ] `efficiency_metric.png`

### Analysis
```bash
# View recommendation
cat "~/Desktop/Dissertation Travelling Santa - Ant Optimization/RECOMMENDATION.txt"

# View summary
cat "~/Desktop/Dissertation Travelling Santa - Ant Optimization/ant_optimization_summary.csv"
```

**Key Findings**:
- Optimal ant count documented
- Efficiency scores available
- Convergence speed trends visible

**Next Step**: Proceed to city scaling experiment.

---

## Experiment 5: City Scaling Analysis

**Estimated Time**: 2-3 hours  
**Purpose**: Understand scaling behavior

### Pre-Execution
- [ ] Clear schedule (2-3 hours uninterrupted)
- [ ] Needs ~15 GB disk space

### Execution
```bash
python city_scaling_experiment.py
```

### Real-Time Monitoring
```bash
# Monitor progress
ls ~/Desktop/Dissertation\ Travelling\ Santa\ -\ City\ Scaling/ | grep cities | wc -l
```

### Verification Checklist (After)
- [ ] Output directory created
- [ ] Subdirectories for each city count (cities_10_run_1, cities_15_run_1, etc.)
- [ ] Key output files:
  - [ ] `city_scaling_summary.csv`
  - [ ] `all_city_scaling_runs.csv`
  - [ ] `ANALYSIS.txt`
  - [ ] `scaling_analysis.png` (main result plot)
  - [ ] `convergence_curves_by_city_count.png`

### Analysis
```bash
# View analysis
cat "~/Desktop/Dissertation Travelling Santa - City Scaling/ANALYSIS.txt"

# Extract key equations
grep "Power law:" "~/Desktop/Dissertation Travelling Santa - City Scaling/ANALYSIS.txt"
grep "R²" "~/Desktop/Dissertation Travelling Santa - City Scaling/ANALYSIS.txt"
```

**Key Findings**:
- Fitted models with equations
- R² goodness-of-fit values
- Complexity classification (O(n^b) or exponential)
- Extrapolation capability

---

## Full Experiment Suite

**Estimated Time**: 10-15 hours total  
**Best**: Run overnight

### Execution
```bash
# Make script executable
chmod +x run_experiments.sh

# Run all experiments
bash run_experiments.sh all
```

### Logging
All output logged to:
```
~/Desktop/Dissertation Travelling Santa - Experiment Logs/
```

### Monitoring (Overnight)
```bash
# Check progress in morning
tail -50 "~/Desktop/Dissertation Travelling Santa - Experiment Logs/"*latest*.log

# Count completed experiments
ls "~/Desktop/Dissertation Travelling Santa - Experiment Logs/" | wc -l
```

---

## Post-Experiment Analysis

### Aggregating Results
```bash
# Compile summary across all experiments
python3 << 'EOF'
import os
import csv

results = {
    'baseline': 'Dissertation Travelling Santa Problem - Distance Only Baseline',
    'multirun': 'Dissertation Travelling Santa - Multi-Run Experiment',
    'ants': 'Dissertation Travelling Santa - Ant Optimization',
    'scaling': 'Dissertation Travelling Santa - City Scaling'
}

for name, dir_base in results.items():
    path = os.path.expanduser(f'~/Desktop/{dir_base}')
    if os.path.exists(path):
        print(f"✓ {name}: {path}")
        # List key files
        for f in os.listdir(path):
            if f.endswith('.csv') or f.endswith('.txt'):
                print(f"  - {f}")
    else:
        print(f"✗ {name}: directory not found")
EOF
```

### Creating Research Output
- [ ] Export summary statistics
- [ ] Prepare figures for publication
- [ ] Document assumptions and parameters
- [ ] Archive all CSVs

### Backup Results
```bash
# Backup all results
tar -czf ~/Desktop/Dissertation_Results_Backup.tar.gz ~/Desktop/Dissertation\ Travelling\ Santa*

# Verify backup
tar -tzf ~/Desktop/Dissertation_Results_Backup.tar.gz | head -20
```

---

## Troubleshooting Guide

### Issue: "No space left on device"
**Solution**:
```bash
# Check disk usage
du -sh ~/Desktop/Dissertation*

# Remove old experiment runs if needed
rm -rf ~/Desktop/Dissertation\ Travelling\ Santa\ Problem\ 50/run_*
```

### Issue: Python module not found
**Solution**:
```bash
pip install --upgrade numpy matplotlib scipy
```

### Issue: Experiment crashes midway
**Solution**:
```bash
# Check last error in output
tail -100 ~/Desktop/Dissertation*/iteration_metrics.csv

# Restart from checkpoint if available
python experiment_runner.py  # Will resume from run numbers already completed
```

### Issue: CSV appears empty
**Solution**:
```bash
# Verify header exists
head -1 ~/Desktop/Dissertation*/iteration_metrics.csv

# Check file size
wc -l ~/Desktop/Dissertation*/iteration_metrics.csv

# If <10 rows, experiment may still be running
```

---

## Final Checklist

After completing all experiments:

- [ ] All 5 experiment directories created
- [ ] Each directory has CSVs with data
- [ ] Visualizations generated
- [ ] Recommendation/Analysis text files present
- [ ] No critical errors in logs
- [ ] Disk usage reasonable
- [ ] Backup created
- [ ] Results reviewed and understood
- [ ] Ready for publication/analysis

---

## Success Indicators

✅ **All Good If**:
- Main run completes without error
- Baseline shows shorter distance than full algorithm
- Multi-run statistics show consistent results (low std dev)
- Ant optimization identifies clear optimal count
- City scaling shows clear mathematical trend

⚠️ **Investigate If**:
- Very high failure rate (penalties in all runs)
- Huge variance across runs (std dev > mean)
- No clear optimal ant count
- Scaling doesn't fit any model well

---

## Documentation Links

- **EXPERIMENT_GUIDE.md** - Detailed experiment descriptions
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation
- **README.md** - Original project overview
- **INDEX.py** - Quick reference guide

---

**Last Updated**: February 16, 2026  
**Status**: Ready for execution
