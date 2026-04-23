"""
Distance-Only ACO Baseline
Minimizes only tour distance (no darkness penalty, no time cost, no work cost).
Used as a comparison baseline for the full TSP variant.
"""
import os
import logging
import numpy as np
import matplotlib.pyplot as plt
import csv
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple

# ==============================================================================
# Logging Configuration
# ==============================================================================
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ==============================================================================
# CONSTANTS AND DEFAULT PARAMETERS
# ==============================================================================
PARENT_EXPERIMENTS_DIR = os.path.expanduser('~/Desktop/Dissertation Travelling Santa Problem')
MAIN_OUTPUT_DIR = os.path.join(PARENT_EXPERIMENTS_DIR, 'distance_only_baseline3')

NUM_ITERATIONS = 60000
PROGRESS_UPDATE_INTERVAL = max(1, int(NUM_ITERATIONS / 100))
NUM_ANTS = 14

# ACO parameters
ALPHA = 3          # pheromone influence
BETA = 2.1         # heuristic influence
RHO = 0.5          # base evaporation rate
Q = 1.0            # pheromone deposit factor
TAU_MIN = 0.1
TAU_MAX = 100.0

# Exploration parameters
INITIAL_EPSILON = 0.45
MIN_EPSILON = 0.05
DECAY_RATE = 0.999962

# Physics parameters for work calculation
AIR_DENSITY = 1.225  # kg/m^3
CROSS_SECTIONAL_AREA = 1.0  # m^2
DEFAULT_SANTA_SPEED_KMPH = 11500  # Constant speed (no constraint-based adjustment)
DEPARTURE_DATETIME_UTC = datetime(2024, 12, 24, 0, 0)  # Start time (for calculating work)


# ==============================================================================
# CITY DATA
# ==============================================================================
cities: List[Dict[str, Any]] = [
    {'name': 'Suva', 'lat': -18.1248, 'lon': 178.4501, 'tz_offset': 12,
     'sunrise': '05:35', 'sunset': '18:45', 'population': 93970},
    {'name': 'Canberra', 'lat': -35.2809, 'lon': 149.1300, 'tz_offset': 10,
     'sunrise': '05:45', 'sunset': '20:15', 'population': 453558},
    {'name': 'Auckland', 'lat': -36.8485, 'lon': 174.7633, 'tz_offset': 12,
     'sunrise': '05:55', 'sunset': '20:40', 'population': 1623000},
    {'name': 'Wellington', 'lat': -41.2865, 'lon': 174.7762, 'tz_offset': 12,
     'sunrise': '05:45', 'sunset': '20:55', 'population': 215400},
    {'name': 'Tokyo', 'lat': 35.6895, 'lon': 139.6917, 'tz_offset': 9,
     'sunrise': '06:48', 'sunset': '16:32', 'population': 37400068},
    {'name': 'Seoul', 'lat': 37.5665, 'lon': 126.9780, 'tz_offset': 9,
     'sunrise': '07:45', 'sunset': '17:15', 'population': 9746000},
    {'name': 'Beijing', 'lat': 39.9042, 'lon': 116.4074, 'tz_offset': 8,
     'sunrise': '07:32', 'sunset': '16:53', 'population': 21540000},
    {'name': 'Shanghai', 'lat': 31.2304, 'lon': 121.4737, 'tz_offset': 8,
     'sunrise': '06:45', 'sunset': '16:55', 'population': 24870000},
    {'name': 'Singapore', 'lat': 1.3521, 'lon': 103.8198, 'tz_offset': 8,
     'sunrise': '07:00', 'sunset': '19:00', 'population': 5453600},
    {'name': 'Nairobi', 'lat': -1.2921, 'lon': 36.8219, 'tz_offset': 3,
     'sunrise': '06:25', 'sunset': '18:40', 'population': 4397000},
    {'name': 'Delhi', 'lat': 28.7041, 'lon': 77.1025, 'tz_offset': 5.5,
     'sunrise': '07:10', 'sunset': '17:26', 'population': 31000000},
    {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777, 'tz_offset': 5.5,
     'sunrise': '06:20', 'sunset': '18:50', 'population': 12478447},
    {'name': 'Dubai', 'lat': 25.2048, 'lon': 55.2708, 'tz_offset': 4,
     'sunrise': '06:45', 'sunset': '17:40', 'population': 3331400},
    {'name': 'Cairo', 'lat': 30.0444, 'lon': 31.2357, 'tz_offset': 2,
     'sunrise': '06:45', 'sunset': '17:00', 'population': 9500000},
    {'name': 'Lagos', 'lat': 6.5244, 'lon': 3.3792, 'tz_offset': 1,
     'sunrise': '06:39', 'sunset': '18:33', 'population': 14368000},
    {'name': 'Cape Town', 'lat': -33.9249, 'lon': 18.4241, 'tz_offset': 2,
     'sunrise': '05:30', 'sunset': '19:55', 'population': 433688},
    {'name': 'Johannesburg', 'lat': -26.2041, 'lon': 28.0473, 'tz_offset': 2,
     'sunrise': '05:15', 'sunset': '19:15', 'population': 957441},
    {'name': 'Moscow', 'lat': 55.7558, 'lon': 37.6173, 'tz_offset': 3,
     'sunrise': '08:58', 'sunset': '15:58', 'population': 12500000},
    {'name': 'Vilnius', 'lat': 54.6872, 'lon': 25.2797, 'tz_offset': 2,
     'sunrise': '08:40', 'sunset': '15:50', 'population': 580020},
    {'name': 'Oslo', 'lat': 59.9139, 'lon': 10.7522, 'tz_offset': 1,
     'sunrise': '09:15', 'sunset': '15:15', 'population': 681067},
    {'name': 'London', 'lat': 51.5074, 'lon': -0.1278, 'tz_offset': 0,
     'sunrise': '08:04', 'sunset': '15:54', 'population': 8982000},
    {'name': 'Lisbon', 'lat': 38.7223, 'lon': -9.1393, 'tz_offset': 0,
     'sunrise': '07:45', 'sunset': '17:30', 'population': 504718},
    {'name': 'Madrid', 'lat': 40.4168, 'lon': -3.7038, 'tz_offset': 1,
     'sunrise': '08:35', 'sunset': '17:55', 'population': 3223000},
    {'name': 'Paris', 'lat': 48.8566, 'lon': 2.3522, 'tz_offset': 1,
     'sunrise': '08:45', 'sunset': '16:55', 'population': 2161000},
    {'name': 'Berlin', 'lat': 52.5200, 'lon': 13.4050, 'tz_offset': 1,
     'sunrise': '08:15', 'sunset': '16:00', 'population': 3644826},
    {'name': 'Chicago', 'lat': 41.8781, 'lon': -87.6298, 'tz_offset': -6,
     'sunrise': '07:15', 'sunset': '16:30', 'population': 2716000},
    {'name': 'Washington, D.C.', 'lat': 38.9072, 'lon': -77.0369, 'tz_offset': -5,
     'sunrise': '07:25', 'sunset': '16:50', 'population': 702455},
    {'name': 'New York City', 'lat': 40.7128, 'lon': -74.0060, 'tz_offset': -5,
     'sunrise': '07:20', 'sunset': '16:35', 'population': 8336817},
    {'name': 'Toronto', 'lat': 43.6532, 'lon': -79.3832, 'tz_offset': -5,
     'sunrise': '07:45', 'sunset': '16:45', 'population': 2930000},
    {'name': 'Ottawa', 'lat': 45.4215, 'lon': -75.6972, 'tz_offset': -5,
     'sunrise': '07:35', 'sunset': '16:25', 'population': 1017449},
    {'name': 'Santiago', 'lat': -33.4489, 'lon': -70.6693, 'tz_offset': -4,
     'sunrise': '06:30', 'sunset': '20:45', 'population': 5743719},
    {'name': 'Buenos Aires', 'lat': -34.6037, 'lon': -58.3816, 'tz_offset': -3,
     'sunrise': '05:40', 'sunset': '20:05', 'population': 2890151},
    {'name': 'Montevideo', 'lat': -34.9011, 'lon': -56.1645, 'tz_offset': -3,
     'sunrise': '05:45', 'sunset': '20:10', 'population': 1380000},
    {'name': 'São Paulo', 'lat': -23.5505, 'lon': -46.6333, 'tz_offset': -3,
     'sunrise': '05:30', 'sunset': '19:00', 'population': 12330000},
    {'name': 'Rio de Janeiro', 'lat': -22.9068, 'lon': -43.1729, 'tz_offset': -3,
     'sunrise': '05:35', 'sunset': '19:05', 'population': 6747000},
    {'name': 'Brasília', 'lat': -15.7939, 'lon': -47.8828, 'tz_offset': -3,
     'sunrise': '05:45', 'sunset': '18:45', 'population': 3055149},
    {'name': 'Bogotá', 'lat': 4.7110, 'lon': -74.0721, 'tz_offset': -5,
     'sunrise': '05:55', 'sunset': '17:55', 'population': 7743955},
    {'name': 'St. Georges', 'lat': 12.0561, 'lon': -61.7486, 'tz_offset': -4,
     'sunrise': '06:25', 'sunset': '17:50', 'population': 33734},
    {'name': 'Mexico City', 'lat': 19.4326, 'lon': -99.1332, 'tz_offset': -6,
     'sunrise': '07:05', 'sunset': '17:55', 'population': 21581000},
    {'name': 'Los Angeles', 'lat': 34.0522, 'lon': -118.2437, 'tz_offset': -8,
     'sunrise': '06:55', 'sunset': '16:50', 'population': 3980400},
    {'name': 'North Pole', 'lat': 90.0000, 'lon': 0.0000, 'tz_offset': 0,
     'sunrise': '00:00', 'sunset': '23:59', 'population': 0},
]

NUM_CITIES = len(cities)
TOTAL_POPULATION = sum(city['population'] for city in cities)

# ==============================================================================
# DISTANCE MATRIX
# ==============================================================================
def haversine_vectorized(coords: np.ndarray) -> np.ndarray:
    R = 6371.0  # Earth's radius in km
    lat_rad = np.radians(coords[:, 0])
    lon_rad = np.radians(coords[:, 1])
    dlat = lat_rad.reshape(-1, 1) - lat_rad.reshape(1, -1)
    dlon = lon_rad.reshape(-1, 1) - lon_rad.reshape(1, -1)
    a = np.sin(dlat / 2) ** 2 + np.cos(lat_rad).reshape(-1, 1) * np.cos(lat_rad).reshape(1, -1) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

city_coords = np.array([(city['lat'], city['lon']) for city in cities])
distance_matrix = haversine_vectorized(city_coords)
np.fill_diagonal(distance_matrix, np.inf)
speed_matrix = np.full((NUM_CITIES, NUM_CITIES), DEFAULT_SANTA_SPEED_KMPH)
pheromone_matrix = np.full((NUM_CITIES, NUM_CITIES), 1.0)

# ==============================================================================
# ANT CLASS (SIMPLIFIED FOR DISTANCE-ONLY)
# ==============================================================================
class DistanceOnlyAnt:
    def __init__(self, start_city: int, epsilon: float = INITIAL_EPSILON) -> None:
        self.start_city = start_city
        self.current_city = start_city
        self.tour: List[int] = [start_city]
        self.allowed_cities: List[int] = [i for i in range(NUM_CITIES) if i != start_city]
        self.tour_length = 0.0
        self.epsilon = epsilon

    def select_next_city(self, pheromone_matrix: np.ndarray) -> Optional[int]:
        if not self.allowed_cities:
            return None

        feasible = self.allowed_cities
        etas = {}
        denom = 0.0

        for idx in feasible:
            dist = distance_matrix[self.current_city][idx]
            eta = (1.0 / dist) ** BETA if dist > 0 else 0.0
            etas[idx] = eta
            tau = pheromone_matrix[self.current_city][idx] ** ALPHA
            denom += tau * eta

        # Epsilon-greedy with decaying epsilon
        if np.random.rand() < self.epsilon:
            return np.random.choice(feasible)
        else:
            probs = [(pheromone_matrix[self.current_city][idx] ** ALPHA * etas[idx]) / denom if denom > 0 else 0.0
                     for idx in feasible]
            return np.random.choice(feasible, p=probs)

    def move_to_city(self, next_city: int) -> None:
        dist = distance_matrix[self.current_city][next_city]
        self.tour_length += dist
        self.tour.append(next_city)
        self.allowed_cities.remove(next_city)
        self.current_city = next_city

    def complete_tour(self) -> None:
        dist = distance_matrix[self.current_city][self.start_city]
        self.tour_length += dist
        self.tour.append(self.start_city)

def get_dynamic_cross_sectional_area(visited_pop: float) -> float:
    """Calculate dynamic cross-sectional area based on visited population."""
    if TOTAL_POPULATION <= 0:
        return CROSS_SECTIONAL_AREA
    fraction_remaining = max(0.0, (TOTAL_POPULATION - visited_pop) / TOTAL_POPULATION)
    return 0.001 + 0.999 * fraction_remaining

def calculate_work_for_tour(tour: List[int]) -> float:
    """
    Calculate total work for a tour using constant speed.
    W = 0.5 * ρ * A * v^2 * d
    
    Returns: total_work (Joules)
    """
    total_work = 0.0
    visited_population = 0.0
    
    for i in range(len(tour) - 1):
        frm, to = tour[i], tour[i+1]
        dist_km = distance_matrix[frm][to]
        dist_m = dist_km * 1000.0  # Convert km to m
        
        # Constant speed (no constraints)
        speed_mps = DEFAULT_SANTA_SPEED_KMPH * (1000.0 / 3600.0)  # Convert km/h to m/s
        dyn_area = get_dynamic_cross_sectional_area(visited_population)
        
        # Calculate work: W = 0.5 * ρ * A * v^2 * d
        work = 0.5 * AIR_DENSITY * dyn_area * (speed_mps ** 2) * dist_m
        total_work += work
        visited_population += cities[to]['population']
    
    return total_work

# ==============================================================================
# ==============================================================================
# PLOTTING FUNCTIONS
# ==============================================================================
def plot_tour(tour: List[int], tour_length: float, filename: str) -> None:
    """Plot the tour on a map with city locations and connections."""
    if not tour:
        return
    
    plt.figure(figsize=(12, 6))
    coords = [(cities[i]['lat'], cities[i]['lon']) for i in tour] + [(cities[tour[0]]['lat'], cities[tour[0]]['lon'])]
    arr = np.array(coords)
    
    # Plot the route
    plt.plot(arr[:, 1], arr[:, 0], 'o-', color='red', markersize=6, linewidth=1.5)
    
    # Add arrows between consecutive cities
    for i in range(len(tour)):
        frm = arr[i]
        to = arr[(i + 1) % len(tour)]
        plt.annotate('', xy=(to[1], to[0]), xytext=(frm[1], frm[0]),
                     arrowprops=dict(arrowstyle='->', lw=1.5, color='gray', alpha=0.6))
    
    # Label cities
    for i, city_idx in enumerate(tour):
        coord = arr[i]
        plt.text(coord[1], coord[0], cities[city_idx]['name'],
                 fontsize=8, ha='right', va='bottom')
    
    plt.title(f"Distance-Only Best Tour: {tour_length:.2f} km")
    plt.xlabel('Longitude')
    plt.ylabel('Latitude')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(filename, dpi=100)
    plt.close()

def plot_convergence(iterations: List[int], best_lengths: List[float], filename: str) -> None:
    plt.figure(figsize=(10, 6))
    plt.plot(iterations, best_lengths, marker='o', linestyle='-')
    plt.xlabel('Iteration')
    plt.ylabel('Best Tour Length (km)')
    plt.title('Distance-Only ACO Convergence')
    plt.grid(True)
    plt.savefig(filename)
    plt.close()

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
def main() -> None:
    global pheromone_matrix

    os.makedirs(MAIN_OUTPUT_DIR, exist_ok=True)

    north_pole_index = next(i for i, c in enumerate(cities) if c['name'] == 'North Pole')
    start_city_index = north_pole_index

    logging.info(f"Start city: {cities[start_city_index]['name']}")

    best_tour: Optional[List[int]] = None
    best_length = np.inf
    best_lengths: List[float] = []

    # Initialize CSV for iteration metrics
    metrics_csv_path = os.path.join(MAIN_OUTPUT_DIR, 'iteration_metrics_distance_only.csv')
    metrics_file = open(metrics_csv_path, 'w', newline='')
    metrics_writer = csv.DictWriter(metrics_file, fieldnames=[
        'Iteration', 'Best Tour Length (km)', 'Best Total Work (J)', 'Epsilon'
    ])
    metrics_writer.writeheader()

    epsilon = INITIAL_EPSILON

    for iteration in range(NUM_ITERATIONS):
        epsilon = max(INITIAL_EPSILON * (DECAY_RATE ** iteration), MIN_EPSILON)
        ants = [DistanceOnlyAnt(start_city=start_city_index, epsilon=epsilon) for _ in range(NUM_ANTS)]

        # Build tours
        for ant in ants:
            while ant.allowed_cities:
                next_city = ant.select_next_city(pheromone_matrix)
                if next_city is None:
                    break
                ant.move_to_city(next_city)
            ant.complete_tour()

            if ant.tour_length < best_length:
                best_tour = ant.tour.copy()
                best_length = ant.tour_length

        # Pheromone evaporation
        dynamic_RHO = RHO * (1 - iteration / NUM_ITERATIONS)
        pheromone_matrix *= (1 - dynamic_RHO)

        # Pheromone deposit by ants
        for ant in ants:
            if ant.tour_length > 0:
                deposit = Q / ant.tour_length
                for i in range(len(ant.tour) - 1):
                    frm, to = ant.tour[i], ant.tour[i+1]
                    pheromone_matrix[frm][to] += deposit
                    pheromone_matrix[to][frm] += deposit

        # Global best deposit
        if best_tour and best_length < np.inf:
            deposit = Q / best_length
            for i in range(len(best_tour) - 1):
                frm, to = best_tour[i], best_tour[i+1]
                pheromone_matrix[frm][to] += deposit
                pheromone_matrix[to][frm] += deposit

        np.clip(pheromone_matrix, TAU_MIN, TAU_MAX, out=pheromone_matrix)

        # Record convergence
        if best_length < np.inf:
            best_lengths.append(best_length)
            # Calculate work for best tour
            work = calculate_work_for_tour(best_tour) if best_tour else 0.0
            
            metrics_writer.writerow({
                'Iteration': iteration + 1,
                'Best Tour Length (km)': round(best_length, 2),
                'Best Total Work (J)': round(work, 2),
                'Epsilon': round(epsilon, 6)
            })
            metrics_file.flush()

        # Progress logging
        if (iteration + 1) % PROGRESS_UPDATE_INTERVAL == 0:
            logging.info(f"Iteration {iteration+1}: Best Length={best_length:.2f} km")
        
        # Plot tour at iteration 1
        if iteration == 0 and best_tour:
            plot_tour(best_tour, best_length, os.path.join(MAIN_OUTPUT_DIR, 'best_tour_iteration_1.png'))
            logging.info("Plotted best tour from iteration 1")

    # Final exports
    if best_tour:
        # Plot final best tour
        plot_tour(best_tour, best_length, os.path.join(MAIN_OUTPUT_DIR, 'best_tour_final.png'))
        logging.info("Plotted final best tour")
        
        # Export best tour
        tour_csv_path = os.path.join(MAIN_OUTPUT_DIR, 'best_tour_distance_only.csv')
        with open(tour_csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['Order', 'City', 'Latitude', 'Longitude'])
            writer.writeheader()
            for i, idx in enumerate(best_tour):
                c = cities[idx]
                writer.writerow({
                    'Order': i+1,
                    'City': c['name'],
                    'Latitude': c['lat'],
                    'Longitude': c['lon']
                })
        logging.info(f"Best tour exported to {tour_csv_path}")

        # Plot convergence
        iterations = list(range(1, len(best_lengths) + 1))
        plot_convergence(iterations, best_lengths, os.path.join(MAIN_OUTPUT_DIR, 'convergence_distance_only.png'))

    metrics_file.close()
    logging.info(f"Distance-only baseline complete. Results saved to {MAIN_OUTPUT_DIR}")

if __name__ == '__main__':
    main()
