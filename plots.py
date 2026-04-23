import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def plot_convergence_dual_axis(csv_file):
    """
    Plot all convergence data on a single plot with dual y-axes.
    - Left y-axis: Distance (red, dashed for Distance Only, solid for TSaP)
    - Right y-axis: Work (blue, dashed for Distance Only, solid for TSaP)
    """
    df = pd.read_csv(csv_file)
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Plot Distance on left y-axis (red)
    ax1.set_xlabel('Iteration')
    ax1.set_ylabel('Distance (km)')
    ax1.plot(df['Iteration'], df['Distance Only Best Tour Length (km)'], 
             color='red', linestyle='--', linewidth=2, label='Distance Only (Length)')
    ax1.plot(df['Iteration'], df['TSaP Best Tour Length (km)'], 
             color='red', linestyle='-', linewidth=2, label='TSaP (Length)')
    
    # Create second y-axis for Work (blue)
    ax2 = ax1.twinx()
    ax2.set_ylabel('Work (J)')
    ax2.plot(df['Iteration'], df['Distance Only Best Total Work (J)'], 
             color='blue', linestyle='--', linewidth=2, label='Distance Only (Work)')
    ax2.plot(df['Iteration'], df['TSaP Best Total Work (J)'], 
             color='blue', linestyle='-', linewidth=2, label='TSaP (Work)')
    
    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper right')
    
    plt.title('Convergence Curves: Distance and Work')
    plt.grid(True)
    fig.tight_layout()
    plt.show()


def plot_convergence_side_by_side(csv_file):
    """
    Plot convergence data in two subplots side by side.
    - Left: Work convergence (blue, dashed for Distance Only, solid for TSaP)
    - Right: Distance convergence (red, dashed for Distance Only, solid for TSaP)
    """
    df = pd.read_csv(csv_file)
    
    fig, (ax_work, ax_distance) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Left plot: Work
    ax_work.plot(df['Iteration'], df['Distance Only Best Total Work (J)'], 
                 color='blue', linestyle='--', linewidth=2, label='Distance Only')
    ax_work.plot(df['Iteration'], df['TSaP Best Total Work (J)'], 
                 color='blue', linestyle='-', linewidth=2, label='TSaP')
    ax_work.set_xlabel('Iteration')
    ax_work.set_ylabel('Work (J)')
    ax_work.set_title('Work Convergence')
    ax_work.legend()
    ax_work.grid(True)
    
    # Right plot: Distance
    ax_distance.plot(df['Iteration'], df['Distance Only Best Tour Length (km)'], 
                     color='red', linestyle='--', linewidth=2, label='Distance Only')
    ax_distance.plot(df['Iteration'], df['TSaP Best Tour Length (km)'], 
                     color='red', linestyle='-', linewidth=2, label='TSaP')
    ax_distance.set_xlabel('Iteration')
    ax_distance.set_ylabel('Distance (km)')
    ax_distance.set_title('Distance Convergence')
    ax_distance.legend()
    ax_distance.grid(True)
    
    plt.suptitle('Convergence Curves Comparison')
    fig.tight_layout()
    plt.show()


if __name__ == '__main__':
    csv_file = '/Users/elliotfisher/Downloads/Things to split - Sheet1-4.csv'
    
    # Create both plots
    plot_convergence_dual_axis(csv_file)
    plot_convergence_side_by_side(csv_file)
