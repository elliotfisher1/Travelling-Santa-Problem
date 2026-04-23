"""
City Scaling Analysis Experiment
Tests how algorithm performance scales with problem size.
Runs simulations for 10, 15, 20, 25 cities with multiple runs each.
Tracks iterations to first viable no-daylight route and fits power-law/exponential curves.
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import csv
import time
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
from scipy.optimize import curve_fit
from scipy import stats

# ==============================================================================
# Configuration
# ==============================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

K_PER_CONTINENT = [1, 2, 3,4,5,6,7,8,9,10]
NUM_RUNS_PER_K = 3  # Multiple runs for statistical significance
NUM_ITERATIONS = 3000
NUM_ANTS = 14  # Number of ants in the colony
VIABLE_THRESHOLD = 1e50
PARENT_EXPERIMENTS_DIR = os.path.expanduser('~/Desktop/Dissertation Travelling Santa Problem')
EXPERIMENT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, f'city_scaling_{NUM_ANTS}_ant_experiment')

# Full cities (60 cities, 10 per continent)
ALL_CITIES = [
    # Oceania (10 cities)
    {'name': 'Sydney', 'lat': -33.8688, 'lon': 151.2093, 'tz_offset': 10,
     'sunrise': '05:30', 'sunset': '20:30', 'population': 5312163, 'continent': 'Oceania'},
    {'name': 'Melbourne', 'lat': -37.8136, 'lon': 144.9631, 'tz_offset': 10,
     'sunrise': '05:45', 'sunset': '20:45', 'population': 4900000, 'continent': 'Oceania'},
    {'name': 'Brisbane', 'lat': -27.4698, 'lon': 153.0251, 'tz_offset': 10,
     'sunrise': '05:40', 'sunset': '20:35', 'population': 2345000, 'continent': 'Oceania'},
    {'name': 'Perth', 'lat': -31.9505, 'lon': 115.8605, 'tz_offset': 8,
     'sunrise': '05:20', 'sunset': '19:40', 'population': 2165000, 'continent': 'Oceania'},
    {'name': 'Canberra', 'lat': -35.2809, 'lon': 149.1300, 'tz_offset': 10,
     'sunrise': '05:45', 'sunset': '20:15', 'population': 453558, 'continent': 'Oceania'},
    {'name': 'Auckland', 'lat': -36.8485, 'lon': 174.7633, 'tz_offset': 12,
     'sunrise': '05:55', 'sunset': '20:40', 'population': 1623000, 'continent': 'Oceania'},
    {'name': 'Wellington', 'lat': -41.2865, 'lon': 174.7762, 'tz_offset': 12,
     'sunrise': '05:45', 'sunset': '20:55', 'population': 215400, 'continent': 'Oceania'},
    {'name': 'Christchurch', 'lat': -43.5321, 'lon': 172.6362, 'tz_offset': 12,
     'sunrise': '05:10', 'sunset': '21:00', 'population': 405000, 'continent': 'Oceania'},
    {'name': 'Fiji', 'lat': -17.7134, 'lon': 178.0650, 'tz_offset': 12,
     'sunrise': '05:50', 'sunset': '20:50', 'population': 896444, 'continent': 'Oceania'},
    {'name': 'Honolulu', 'lat': 21.3099, 'lon': -157.8581, 'tz_offset': -10,
     'sunrise': '06:30', 'sunset': '18:45', 'population': 374676, 'continent': 'Oceania'},
    # Asia (10 cities)
    # Asia (10 cities)
    {'name': 'Tokyo', 'lat': 35.6895, 'lon': 139.6917, 'tz_offset': 9,
     'sunrise': '06:48', 'sunset': '16:32', 'population': 37400068, 'continent': 'Asia'},
    {'name': 'Seoul', 'lat': 37.5665, 'lon': 126.9780, 'tz_offset': 9,
     'sunrise': '07:45', 'sunset': '17:15', 'population': 9746000, 'continent': 'Asia'},
    {'name': 'Beijing', 'lat': 39.9042, 'lon': 116.4074, 'tz_offset': 8,
     'sunrise': '07:32', 'sunset': '16:53', 'population': 21540000, 'continent': 'Asia'},
    {'name': 'Shanghai', 'lat': 31.2304, 'lon': 121.4737, 'tz_offset': 8,
     'sunrise': '06:45', 'sunset': '16:55', 'population': 24870000, 'continent': 'Asia'},
    {'name': 'Singapore', 'lat': 1.3521, 'lon': 103.8198, 'tz_offset': 8,
     'sunrise': '07:00', 'sunset': '19:00', 'population': 5453600, 'continent': 'Asia'},
    {'name': 'Delhi', 'lat': 28.7041, 'lon': 77.1025, 'tz_offset': 5.5,
     'sunrise': '07:10', 'sunset': '17:26', 'population': 31000000, 'continent': 'Asia'},
    {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'tz_offset': 5.5,
     'sunrise': '06:20', 'sunset': '18:50', 'population': 12478447, 'continent': 'Asia'},
    {'name': 'Dubai', 'lat': 25.2048, 'lon': 55.2708, 'tz_offset': 4,
     'sunrise': '06:45', 'sunset': '17:40', 'population': 3331400, 'continent': 'Asia'},
    {'name': 'Bangkok', 'lat': 13.7563, 'lon': 100.5018, 'tz_offset': 7,
     'sunrise': '06:15', 'sunset': '18:15', 'population': 10156000, 'continent': 'Asia'},
    {'name': 'Manila', 'lat': 14.5994, 'lon': 120.9842, 'tz_offset': 8,
     'sunrise': '06:20', 'sunset': '18:20', 'population': 13484462, 'continent': 'Asia'},
    # Africa (10 cities)
    {'name': 'Cairo', 'lat': 30.0444, 'lon': 31.2357, 'tz_offset': 2,
     'sunrise': '06:45', 'sunset': '17:00', 'population': 9500000, 'continent': 'Africa'},
    {'name': 'Lagos', 'lat': 6.5244, 'lon': 3.3792, 'tz_offset': 1,
     'sunrise': '06:39', 'sunset': '18:33', 'population': 14368000, 'continent': 'Africa'},
    {'name': 'Cape Town', 'lat': -33.9249, 'lon': 18.4241, 'tz_offset': 2,
     'sunrise': '05:30', 'sunset': '19:55', 'population': 433688, 'continent': 'Africa'},
    {'name': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'tz_offset': 2,
     'sunrise': '05:15', 'sunset': '19:15', 'population': 957441, 'continent': 'Africa'},
    {'name': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219, 'tz_offset': 3,
     'sunrise': '06:25', 'sunset': '18:40', 'population': 4397000, 'continent': 'Africa'},
    {'name': 'Accra', 'lat': 5.6037, 'lon': -0.1870, 'tz_offset': 0,
     'sunrise': '06:35', 'sunset': '18:35', 'population': 2327000, 'continent': 'Africa'},
    {'name': 'Khartoum', 'lat': 15.5007, 'lon': 32.5599, 'tz_offset': 2,
     'sunrise': '07:00', 'sunset': '17:30', 'population': 5274000, 'continent': 'Africa'},
    {'name': 'Dar es Salaam', 'lat': -6.8000, 'lon': 39.2833, 'tz_offset': 3,
     'sunrise': '06:15', 'sunset': '18:45', 'population': 4364541, 'continent': 'Africa'},
    {'name': 'Addis Ababa', 'lat': 9.0320, 'lon': 38.7469, 'tz_offset': 3,
     'sunrise': '06:30', 'sunset': '18:30', 'population': 5228000, 'continent': 'Africa'},
    {'name': 'Casablanca', 'lat': 33.5731, 'lon': -7.5898, 'tz_offset': 0,
     'sunrise': '07:10', 'sunset': '17:40', 'population': 3359818, 'continent': 'Africa'},
    # Europe (10 cities)
    {'name': 'Moscow', 'lat': 55.7558, 'lon': 37.6173, 'tz_offset': 3,
     'sunrise': '08:58', 'sunset': '15:58', 'population': 12500000, 'continent': 'Europe'},
    {'name': 'London', 'lat': 51.5074, 'lon': -0.1278, 'tz_offset': 0,
     'sunrise': '08:04', 'sunset': '15:54', 'population': 8982000, 'continent': 'Europe'},
    {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522, 'tz_offset': 1,
     'sunrise': '08:45', 'sunset': '16:55', 'population': 2161000, 'continent': 'Europe'},
    {'name': 'Berlin', 'lat': 52.5200, 'lon': 13.4050, 'tz_offset': 1,
     'sunrise': '08:15', 'sunset': '16:00', 'population': 3644826, 'continent': 'Europe'},
    {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038, 'tz_offset': 1,
     'sunrise': '08:35', 'sunset': '17:55', 'population': 3223000, 'continent': 'Europe'},
    {'name': 'Rome', 'lat': 41.9028, 'lon': 12.4964, 'tz_offset': 1,
     'sunrise': '07:55', 'sunset': '17:15', 'population': 2761477, 'continent': 'Europe'},
    {'name': 'Amsterdam', 'lat': 52.3676, 'lon': 4.9041, 'tz_offset': 1,
     'sunrise': '08:30', 'sunset': '16:30', 'population': 873000, 'continent': 'Europe'},
    {'name': 'Istanbul', 'lat': 41.0082, 'lon': 28.9784, 'tz_offset': 3,
     'sunrise': '07:00', 'sunset': '17:15', 'population': 15840000, 'continent': 'Europe'},
    {'name': 'Athens', 'lat': 37.9838, 'lon': 23.7275, 'tz_offset': 2,
     'sunrise': '06:50', 'sunset': '17:00', 'population': 3154000, 'continent': 'Europe'},
    {'name': 'Prague', 'lat': 50.0755, 'lon': 14.4378, 'tz_offset': 1,
     'sunrise': '08:20', 'sunset': '15:45', 'population': 1324000, 'continent': 'Europe'},
    # North America (10 cities)
    {'name': 'Chicago', 'lat': 41.8781, 'lon': -87.6298, 'tz_offset': -6,
     'sunrise': '07:15', 'sunset': '16:30', 'population': 2716000, 'continent': 'North America'},
    {'name': 'New York City', 'lat': 40.7128, 'lon': -74.0060, 'tz_offset': -5,
     'sunrise': '07:20', 'sunset': '16:35', 'population': 8336817, 'continent': 'North America'},
    {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437, 'tz_offset': -8,
     'sunrise': '06:55', 'sunset': '16:50', 'population': 3980400, 'continent': 'North America'},
    {'name': 'Washington, D.C.', 'lat': 38.9072, 'lon': -77.0369, 'tz_offset': -5,
     'sunrise': '07:25', 'sunset': '16:50', 'population': 702455, 'continent': 'North America'},
    {'name': 'Toronto', 'lat': 43.6532, 'lon': -79.3832, 'tz_offset': -5,
     'sunrise': '07:45', 'sunset': '16:45', 'population': 2930000, 'continent': 'North America'},
    {'name': 'Vancouver', 'lat': 49.2827, 'lon': -123.1207, 'tz_offset': -8,
     'sunrise': '07:30', 'sunset': '16:20', 'population': 675000, 'continent': 'North America'},
    {'name': 'Mexico City', 'lat': 19.4326, 'lon': -99.1332, 'tz_offset': -6,
     'sunrise': '07:05', 'sunset': '17:55', 'population': 21581000, 'continent': 'North America'},
    {'name': 'Ottawa', 'lat': 45.4215, 'lon': -75.6972, 'tz_offset': -5,
     'sunrise': '07:35', 'sunset': '16:25', 'population': 1017449, 'continent': 'North America'},
    {'name': 'St. Georges', 'lat': 12.0561, 'lon': -61.7486, 'tz_offset': -4,
     'sunrise': '06:25', 'sunset': '17:50', 'population': 33734, 'continent': 'North America'},
    {'name': 'Havana', 'lat': 23.1136, 'lon': -82.3666, 'tz_offset': -5,
     'sunrise': '06:55', 'sunset': '17:45', 'population': 2106146, 'continent': 'North America'},
    # South America (10 cities)
    {'name': 'São Paulo', 'lat': -23.5505, 'lon': -46.6333, 'tz_offset': -3,
     'sunrise': '05:30', 'sunset': '19:00', 'population': 12330000, 'continent': 'South America'},
    {'name': 'Rio de Janeiro', 'lat': -22.9068, 'lon': -43.1729, 'tz_offset': -3,
     'sunrise': '05:35', 'sunset': '19:05', 'population': 6747000, 'continent': 'South America'},
    {'name': 'Buenos Aires', 'lat': -34.6037, 'lon': -58.3816, 'tz_offset': -3,
     'sunrise': '05:40', 'sunset': '20:05', 'population': 2890151, 'continent': 'South America'},
    {'name': 'Brasília', 'lat': -15.7939, 'lon': -47.8828, 'tz_offset': -3,
     'sunrise': '05:45', 'sunset': '18:45', 'population': 3055149, 'continent': 'South America'},
    {'name': 'Bogotá', 'lat': 4.7110, 'lon': -74.0721, 'tz_offset': -5,
     'sunrise': '05:55', 'sunset': '17:55', 'population': 7743955, 'continent': 'South America'},
    {'name': 'Lima', 'lat': -12.0464, 'lon': -77.0428, 'tz_offset': -5,
     'sunrise': '05:50', 'sunset': '17:45', 'population': 9130000, 'continent': 'South America'},
    {'name': 'Santiago', 'lat': -33.4489, 'lon': -70.6693, 'tz_offset': -4,
     'sunrise': '06:30', 'sunset': '20:45', 'population': 5743719, 'continent': 'South America'},
    {'name': 'Montevideo', 'lat': -34.9011, 'lon': -56.1645, 'tz_offset': -3,
     'sunrise': '05:45', 'sunset': '20:10', 'population': 1380000, 'continent': 'South America'},
    {'name': 'Quito', 'lat': -0.2299, 'lon': -78.5099, 'tz_offset': -5,
     'sunrise': '06:00', 'sunset': '18:00', 'population': 1700000, 'continent': 'South America'},
    {'name': 'Asunción', 'lat': -25.2637, 'lon': -57.5759, 'tz_offset': -4,
     'sunrise': '05:35', 'sunset': '19:50', 'population': 1882000, 'continent': 'South America'},
    {'name': 'North Pole', 'lat': 90.0000, 'lon': 0.0000, 'tz_offset': 0,
     'sunrise': '00:00', 'sunset': '23:59', 'population': 0, 'continent': 'Arctic'},
]

# Group cities by continent and order them
from collections import defaultdict
continent_groups = defaultdict(list)
for city in ALL_CITIES[:-1]:  # Exclude North Pole
    continent_groups[city['continent']].append(city)

# Sort continents alphabetically, excluding Arctic
continents_order = sorted([c for c in continent_groups.keys() if c != 'Arctic'])

# Create ordered cities list (but we'll select proportionally)
# For this experiment, we'll select k cities from each continent

def get_cities_subset(k_per_continent: int) -> List[Dict[str, Any]]:
    """Get k cities from each continent, always including North Pole."""
    selected = []
    for cont in continents_order:
        cities_in_cont = continent_groups[cont]
        num_to_take = min(k_per_continent, len(cities_in_cont))
        selected.extend(cities_in_cont[:num_to_take])
    selected.append(ALL_CITIES[-1])  # North Pole
    return selected

# ==============================================================================
# UTILITY: Generate city subset and run experiment
# ==============================================================================

def run_city_scaling_experiment(k_per_continent: int, run_num: int, experiment_dir: str) -> Dict[str, Any]:
    """
    Run TSP algorithm with k cities per continent.
    Returns dictionary with metrics including iterations to viable route.
    """
    cities = get_cities_subset(k_per_continent)
    n_cities = len(cities)
    
    # Read the main script
    with open("/Users/elliotfisher/Travelling-Santa-Problem-1/main.py", 'r') as f:
        main_code = f.read()
    
    # Modify for this experiment
    main_code = main_code.replace(
        "MAIN_OUTPUT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'main_run_4 ')",
        f"MAIN_OUTPUT_DIR = '{experiment_dir}'"
    )
    main_code = main_code.replace(
        "NUM_ITERATIONS = 1000",
        "NUM_ITERATIONS = 2000"
    )
    main_code = main_code.replace(
        "VIABLE_THRESHOLD = 1e6",
        f"VIABLE_THRESHOLD = {VIABLE_THRESHOLD}"
    )
    
    # Replace cities list
    cities_str = "cities: List[Dict[str, Any]] = [\n"
    for city in cities[:-1]:  # All but North Pole
        cities_str += f"    {repr(city)},\n"
    cities_str += f"    {repr(cities[-1])},\n"
    cities_str += "]"
    
    # Find and replace the cities definition
    import re
    pattern = r"cities: List\[Dict\[str, Any\]\] = \[.*?\n\]"
    main_code = re.sub(pattern, cities_str, main_code, flags=re.DOTALL, count=1)
    
    # Execute
    start_time = time.time()
    exec_globals = {'__name__': '__main__'}
    try:
        exec(main_code, exec_globals)
    except Exception as e:
        logging.error(f"Execution failed: {e}")
        return {
            'k_per_continent': k_per_continent,
            'n_cities': n_cities,
            'run': run_num,
            'runtime_seconds': time.time() - start_time,
            'iterations_to_viable': None,
            'final_effective_cost': None
        }
    
    end_time = time.time()
    runtime = end_time - start_time
    
    # Extract metrics
    metrics_csv = os.path.join(experiment_dir, 'iteration_metrics.csv')
    
    results = {
        'k_per_continent': k_per_continent,
        'n_cities': n_cities,
        'run': run_num,
        'runtime_seconds': runtime,
        'iterations_to_viable': None,
        'final_effective_cost': None
    }
    
    if os.path.exists(metrics_csv):
        with open(metrics_csv, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            
            # Find first iteration reaching viable threshold (cost < 10^14)
            for row in rows:
                try:
                    iteration = int(row['Iteration'])
                    effective_cost = float(row['Best Effective Cost (J)'])
                    if effective_cost < VIABLE_THRESHOLD and results['iterations_to_viable'] is None:
                        results['iterations_to_viable'] = iteration
                        logging.info(f"Found viable solution at iteration {iteration} with cost {effective_cost:.2e}")
                except (ValueError, KeyError) as e:
                    logging.warning(f"Error parsing row: {row}, error: {e}")
            
            # Final metrics
            if rows:
                last_row = rows[-1]
                results['final_effective_cost'] = float(last_row['Best Effective Cost (J)'])
    else:
        logging.warning(f"Metrics CSV not found at {metrics_csv}")
    
    return results

# ==============================================================================
# FITTING FUNCTIONS
# ==============================================================================
def power_law(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Power law: y = a * x^b"""
    return a * np.power(x, b)

def exponential(x: np.ndarray, a: float, b: float) -> np.ndarray:
    """Exponential: y = a * exp(b*x)"""
    return a * np.exp(b * x)

def polynomial_quadratic(x: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """Quadratic: y = a + b*x + c*x^2"""
    return a + b * x + c * np.power(x, 2)

# ==============================================================================
# PLOTTING FUNCTIONS
# ==============================================================================
def save_summary_for_k(k: int, n_cities: int, iterations: List[float], runtimes: List[float], experiment_dir: str) -> None:
    """Save a summary file after completing all runs for a specific k value."""
    summary_file = os.path.join(experiment_dir, f'summary_k_{k}.txt')
    
    viable_runs = len(iterations)
    total_runs = NUM_RUNS_PER_K
    
    with open(summary_file, 'w') as f:
        f.write(f"SUMMARY FOR k={k} ({n_cities} total cities)\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Completed: {viable_runs}/{total_runs} runs found viable routes\n\n")
        
        if iterations:
            f.write("ITERATIONS TO VIABLE:\n")
            f.write(f"  Average: {np.mean(iterations):.2f}\n")
            f.write(f"  Std deviation: {np.std(iterations):.2f}\n")
            f.write(f"  Min: {np.min(iterations):.0f}\n")
            f.write(f"  Max: {np.max(iterations):.0f}\n")
            f.write(f"  Median: {np.median(iterations):.2f}\n")
        else:
            f.write("No viable routes found for this k value.\n")
        
        if runtimes:
            f.write("\nRUNTIME (seconds):\n")
            f.write(f"  Average: {np.mean(runtimes):.2f}s\n")
            f.write(f"  Std deviation: {np.std(runtimes):.2f}s\n")
            f.write(f"  Min: {np.min(runtimes):.2f}s\n")
            f.write(f"  Max: {np.max(runtimes):.2f}s\n")
            f.write(f"  Total: {np.sum(runtimes):.2f}s\n")
    
    logging.info(f"Saved summary for k={k} to {summary_file}")

def save_fit_stats_to_csv(k_list: List[int], iterations_data: List[List[float]], fit_stats: Dict[str, Any], filename: str) -> None:
    """Save scaling analysis fit statistics to CSV."""
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Scaling Analysis Results'])
        writer.writerow([])
        
        # Data summary
        writer.writerow(['K per Continent', 'Mean Iterations', 'Std Dev', 'Min', 'Max', 'Median', 'N Runs'])
        for k, data in zip(k_list, iterations_data):
            valid_data = [d for d in data if d is not None]
            if valid_data:
                writer.writerow([
                    k,
                    f"{np.mean(valid_data):.2f}",
                    f"{np.std(valid_data):.2f}",
                    f"{np.min(valid_data):.0f}",
                    f"{np.max(valid_data):.0f}",
                    f"{np.median(valid_data):.2f}",
                    len(valid_data)
                ])
            else:
                writer.writerow([k, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 0])
        
        writer.writerow([])
        writer.writerow(['Curve Fit Models'])
        writer.writerow([])
        
        # Power law fit
        if 'power_law' in fit_stats:
            params = fit_stats['power_law']['params']
            r2 = fit_stats['power_law']['r2']
            writer.writerow(['Model', 'Equation', 'R²', 'Param A', 'Param B'])
            writer.writerow(['Power Law', f'y = {params[0]:.4f} * x^{params[1]:.4f}', f'{r2:.4f}', f'{params[0]:.4f}', f'{params[1]:.4f}'])
        
        # Exponential fit
        if 'exponential' in fit_stats:
            params = fit_stats['exponential']['params']
            r2 = fit_stats['exponential']['r2']
            writer.writerow(['Exponential', f'y = {params[0]:.4f} * exp({params[1]:.4f}*x)', f'{r2:.4f}', f'{params[0]:.4f}', f'{params[1]:.4f}'])
        
        # Quadratic fit
        if 'quadratic' in fit_stats:
            params = fit_stats['quadratic']['params']
            r2 = fit_stats['quadratic']['r2']
            writer.writerow(['Quadratic', f'y = {params[0]:.4f} + {params[1]:.4f}*x + {params[2]:.4f}*x²', f'{r2:.4f}', f'{params[0]:.4f}', f'{params[1]:.4f}', f'{params[2]:.4f}'])

def plot_scaling_with_fits(k_list: List[int], iterations_data: List[List[float]], filename: str) -> Dict[str, Any]:
    """
    Plot iterations to viable vs city count with multiple fit curves.
    Returns fit statistics.
    """
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Calculate mean and std for each city count
    means = []
    stds = []
    for data in iterations_data:
        valid_data = [d for d in data if d is not None]
        if valid_data:
            means.append(np.mean(valid_data))
            stds.append(np.std(valid_data))
        else:
            means.append(None)
            stds.append(None)
    
    # Plot data with error bars
    valid_indices = [i for i, m in enumerate(means) if m is not None]
    valid_k = [k_list[i] for i in valid_indices]
    valid_means = [means[i] for i in valid_indices]
    valid_stds = [stds[i] for i in valid_indices]
    
    ax.errorbar(valid_k, valid_means, yerr=valid_stds, fmt='o', capsize=5, capthick=2,
               label='Data (mean ± std)', markersize=8)
    
    fit_stats = {}
    
    # Try different fits
    if len(valid_k) >= 2:
        try:
            # Power law fit
            popt_power, _ = curve_fit(power_law, np.array(valid_k), np.array(valid_means),
                                     p0=[1, 1], maxfev=5000)
            power_curve = power_law(np.array(valid_k), *popt_power)
            r2_power = 1 - np.sum((np.array(valid_means) - power_curve)**2) / np.sum((np.array(valid_means) - np.mean(valid_means))**2)
            ax.plot(valid_k, power_curve, '--', label=f'Power Law (R²={r2_power:.4f})', linewidth=2)
            fit_stats['power_law'] = {'params': popt_power, 'r2': r2_power}
            logging.info(f"Power law: y = {popt_power[0]:.4f} * x^{popt_power[1]:.4f}, R²={r2_power:.4f}")
        except Exception as e:
            logging.warning(f"Power law fit failed: {e}")
        
        try:
            # Exponential fit
            popt_exp, _ = curve_fit(exponential, np.array(valid_k), np.array(valid_means),
                                   p0=[1, 0.1], maxfev=5000)
            exp_curve = exponential(np.array(valid_k), *popt_exp)
            r2_exp = 1 - np.sum((np.array(valid_means) - exp_curve)**2) / np.sum((np.array(valid_means) - np.mean(valid_means))**2)
            ax.plot(valid_k, exp_curve, ':', label=f'Exponential (R²={r2_exp:.4f})', linewidth=2)
            fit_stats['exponential'] = {'params': popt_exp, 'r2': r2_exp}
            logging.info(f"Exponential: y = {popt_exp[0]:.4f} * exp({popt_exp[1]:.4f}*x), R²={r2_exp:.4f}")
        except Exception as e:
            logging.warning(f"Exponential fit failed: {e}")
        
        try:
            # Quadratic fit
            popt_quad, _ = curve_fit(polynomial_quadratic, np.array(valid_k), np.array(valid_means),
                                    p0=[1, 1, 1], maxfev=5000)
            quad_curve = polynomial_quadratic(np.array(valid_k), *popt_quad)
            r2_quad = 1 - np.sum((np.array(valid_means) - quad_curve)**2) / np.sum((np.array(valid_means) - np.mean(valid_means))**2)
            ax.plot(valid_k, quad_curve, '-.', label=f'Quadratic (R²={r2_quad:.4f})', linewidth=2)
            fit_stats['quadratic'] = {'params': popt_quad, 'r2': r2_quad}
            logging.info(f"Quadratic: y = {popt_quad[0]:.4f} + {popt_quad[1]:.4f}*x + {popt_quad[2]:.4f}*x², R²={r2_quad:.4f}")
        except Exception as e:
            logging.warning(f"Quadratic fit failed: {e}")
    
    ax.set_xlabel('Cities per Continent', fontsize=12)
    ax.set_ylabel('Iterations to Viable Route', fontsize=12)
    ax.set_title('Scaling of Convergence Time with Cities per Continent', fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=150)
    plt.close()
    
    return fit_stats

def plot_convergence_curves_by_city_count(all_results: List[Dict[str, Any]], experiment_dir: str) -> None:
    """Plot convergence curves for a few representative runs from each city count."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    n_cities_list = [8, 15, 22]
    for idx, city_count in enumerate(n_cities_list):
        ax = axes[idx]
        runs = [r for r in all_results if r['n_cities'] == city_count]
        
        for run_idx, run_result in enumerate(runs[:2]):  # Plot first 2 runs for each city count
            run_num = run_result['run']
            run_dir = os.path.join(experiment_dir, f'k_{(city_count-1)//7}_run_{run_num}')
            metrics_csv = os.path.join(run_dir, 'iteration_metrics.csv')
            
            if os.path.exists(metrics_csv):
                with open(metrics_csv, 'r') as f:
                    reader = csv.DictReader(f)
                    costs = []
                    iterations = []
                    for row in reader:
                        iterations.append(int(row['Iteration']))
                        costs.append(float(row['Best Effective Cost (J)']))
                
                ax.plot(iterations, costs, alpha=0.7, label=f'Run {run_num}')
        
        ax.axhline(y=VIABLE_THRESHOLD, color='r', linestyle='--', label='Viable threshold')
        ax.set_xlabel('Iteration')
        ax.set_ylabel('Effective Cost (J)')
        ax.set_title(f'{city_count} Cities')
        ax.set_yscale('log')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(os.path.join(experiment_dir, 'convergence_curves_by_city_count.png'), dpi=150)
    plt.close()

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main() -> None:
    os.makedirs(EXPERIMENT_DIR, exist_ok=True)
    
    logging.info(f"Starting city scaling experiment")
    logging.info(f"Testing k per continent: {K_PER_CONTINENT}")
    logging.info(f"Runs per k: {NUM_RUNS_PER_K}")
    
    all_results: List[Dict[str, Any]] = []
    iterations_by_k: Dict[int, List[float]] = {k: [] for k in K_PER_CONTINENT}
    runtimes_by_k: Dict[int, List[float]] = {k: [] for k in K_PER_CONTINENT}
    
    # Run experiments
    total_runs = len(K_PER_CONTINENT) * NUM_RUNS_PER_K
    run_count = 0
    
    for k in K_PER_CONTINENT:
        n_cities = k * 7 + 1
        logging.info(f"\nTesting with {k} cities per continent ({n_cities} total)...")
        
        for run_num in range(1, NUM_RUNS_PER_K + 1):
            run_count += 1
            logging.info(f"  Run {run_num}/{NUM_RUNS_PER_K} (overall {run_count}/{total_runs})")
            
            exp_dir = os.path.join(EXPERIMENT_DIR, f'k_{k}_run_{run_num}')
            
            try:
                results = run_city_scaling_experiment(k, run_num, exp_dir)
                results['k_per_continent'] = k
                results['n_cities'] = n_cities
                all_results.append(results)
                
                runtimes_by_k[k].append(results['runtime_seconds'])
                
                if results['iterations_to_viable']:
                    iterations_by_k[k].append(results['iterations_to_viable'])
                    cost_str = f"{results['final_effective_cost']:.2e}" if results['final_effective_cost'] else "N/A"
                    logging.info(f"    ✓ Viable at iteration {results['iterations_to_viable']} (cost: {cost_str} J)")
                else:
                    cost_str = f"{results['final_effective_cost']:.2e}" if results['final_effective_cost'] else "N/A"
                    logging.info(f"    ✗ No viable route found (best cost: {cost_str} J)")
                
            except Exception as e:
                logging.error(f"  Run failed: {e}")
        
        # Save summary after completing all runs for this k
        save_summary_for_k(k, n_cities, iterations_by_k[k], runtimes_by_k[k], EXPERIMENT_DIR)
    
    # Generate summary statistics
    summary_csv = os.path.join(EXPERIMENT_DIR, 'city_scaling_summary.csv')
    with open(summary_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'K per Continent', 'Total Cities', 'Total Runs', 'Viable Runs', 'Avg Iterations to Viable',
            'Std Iterations', 'Min Iterations', 'Max Iterations'
        ])
        writer.writeheader()
        
        for k in K_PER_CONTINENT:
            iters = iterations_by_k[k]
            total_runs = NUM_RUNS_PER_K
            viable_runs = len(iters)
            n_cities = k * 7 + 1
            
            writer.writerow({
                'K per Continent': k,
                'Total Cities': n_cities,
                'Total Runs': total_runs,
                'Viable Runs': viable_runs,
                'Avg Iterations to Viable': round(np.mean(iters), 2) if iters else 'N/A',
                'Std Iterations': round(np.std(iters), 2) if iters else 'N/A',
                'Min Iterations': round(np.min(iters), 2) if iters else 'N/A',
                'Max Iterations': round(np.max(iters), 2) if iters else 'N/A'
            })
    
    # Export detailed results
    detailed_csv = os.path.join(EXPERIMENT_DIR, 'all_city_scaling_runs.csv')
    with open(detailed_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'K per Continent', 'Total Cities', 'Run Number', 'Iterations to Viable',
            'Final Effective Cost (J)', 'Runtime (s)'
        ])
        writer.writeheader()
        
        for result in all_results:
            writer.writerow({
                'K per Continent': result['k_per_continent'],
                'Total Cities': result['n_cities'],
                'Run Number': result['run'],
                'Iterations to Viable': result['iterations_to_viable'] if result['iterations_to_viable'] else 'N/A',
                'Final Effective Cost (J)': round(result['final_effective_cost'], 2) if result['final_effective_cost'] else 'N/A',
                'Runtime (s)': round(result['runtime_seconds'], 2)
            })
    
    # Generate main scaling plot with fits
    k_list = K_PER_CONTINENT
    iterations_data = [iterations_by_k[k] for k in k_list]
    scaling_plot = os.path.join(EXPERIMENT_DIR, 'scaling_analysis.png')
    fit_stats = plot_scaling_with_fits(k_list, iterations_data, scaling_plot)
    
    # Export fit stats to CSV
    scaling_csv = os.path.join(EXPERIMENT_DIR, 'scaling_analysis.csv')
    save_fit_stats_to_csv(k_list, iterations_data, fit_stats, scaling_csv)
    
    # Generate convergence curves
    plot_convergence_curves_by_city_count(all_results, EXPERIMENT_DIR)
    
    # Write analysis report
    analysis_file = os.path.join(EXPERIMENT_DIR, 'ANALYSIS.txt')
    with open(analysis_file, 'w') as f:
        f.write("CITY SCALING ANALYSIS\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("SUMMARY\n")
        f.write("-" * 80 + "\n")
        for k in K_PER_CONTINENT:
            iters = iterations_by_k[k]
            n_cities = k * 7 + 1
            if iters:
                f.write(f"{k} cities per continent ({n_cities} total): avg {np.mean(iters):.0f} ± {np.std(iters):.0f} iterations\n")
            else:
                f.write(f"{k} cities per continent ({n_cities} total): no viable routes found\n")
        
        f.write("\n\nFIT ANALYSIS\n")
        f.write("-" * 80 + "\n")
        
        if 'power_law' in fit_stats:
            params = fit_stats['power_law']['params']
            r2 = fit_stats['power_law']['r2']
            f.write(f"Power Law: y = {params[0]:.4f} * x^{params[1]:.4f}\n")
            f.write(f"  R² = {r2:.6f}\n")
            f.write(f"  Interpretation: Convergence time scales as O(n^{params[1]:.2f})\n\n")
        
        if 'exponential' in fit_stats:
            params = fit_stats['exponential']['params']
            r2 = fit_stats['exponential']['r2']
            f.write(f"Exponential: y = {params[0]:.4f} * exp({params[1]:.4f}*x)\n")
            f.write(f"  R² = {r2:.6f}\n")
            f.write(f"  Interpretation: Convergence time scales exponentially\n\n")
        
        if 'quadratic' in fit_stats:
            params = fit_stats['quadratic']['params']
            r2 = fit_stats['quadratic']['r2']
            f.write(f"Quadratic: y = {params[0]:.4f} + {params[1]:.4f}*x + {params[2]:.4f}*x²\n")
            f.write(f"  R² = {r2:.6f}\n")
            f.write(f"  Interpretation: Convergence time follows quadratic polynomial\n\n")
        
        f.write("\n\nRECOMMENDATIONS\n")
        f.write("-" * 80 + "\n")
        f.write("1. Use the scaling relationship to predict convergence time for larger problems\n")
        f.write("2. Consider hybrid approaches or early stopping for larger city counts\n")
        f.write("3. The viable threshold (cost < 10^14) may need adjustment for larger problems\n")
    
    logging.info(f"\nExperiment complete! Results saved to {EXPERIMENT_DIR}")
    logging.info(f"Summary CSV: {summary_csv}")
    logging.info(f"Detailed CSV: {detailed_csv}")
    logging.info(f"Scaling plot: {scaling_plot}")
    logging.info(f"Analysis report: {analysis_file}")

if __name__ == '__main__':
    main()
