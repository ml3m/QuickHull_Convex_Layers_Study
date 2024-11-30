import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tracemalloc
from convexhull_quickhull_implementation import ConvexHull_QuickHull as ConvexHull
from config import *

# For reproducibility
if not PERMIT_RANDOM_SEED:
    np.random.seed(RANDOM_SEED)  

def generate_grid_points(grid_size, x_range, y_range):
    """
    Generate points in a grid format based on the specified grid size and ranges.
    """
    x_values = np.linspace(0, x_range, grid_size)
    y_values = np.linspace(0, y_range, grid_size)
    
    x_grid, y_grid = np.meshgrid(x_values, y_values)
    points = np.vstack([x_grid.ravel(), y_grid.ravel()]).T
    return points

def compute_convex_layers(points):
    """
    Compute convex layers using the QuickHull algorithm.
    """
    layers = []
    remaining_points = points.copy()
    
    while len(remaining_points) > 0:
        if len(remaining_points) >= 3:
            hull = ConvexHull(remaining_points)
            layers.append(remaining_points[hull.vertices])
            remaining_points = np.delete(remaining_points, hull.vertices, axis=0)
        else:
            if len(remaining_points) == 2:
                layers.append(remaining_points)
            elif len(remaining_points) == 1:
                layers.append(remaining_points)
            remaining_points = np.array([])  # Clear remaining points
            
    return layers

def generate_collinear_points(n, x_range=1000):
    """
    Generate n collinear points along the x-axis (y = 0).
    """
    x = np.linspace(0, x_range, n)
    y = np.linspace(500, 500, n)
    return np.vstack([x, y]).T

# Memory and time tracking
if __name__ == "__main__":
    for points_in_list in POINTS_LIST:

        # Start memory tracking
        tracemalloc.start()

        # Generate points
        points = np.random.rand(points_in_list, 2) * POINTS_RANGE

        # Snapshot memory usage before convex layer computation
        snapshot_before = tracemalloc.take_snapshot()

        # Measure computation time
        start_time = time.time()
        convex_layers = compute_convex_layers(points)
        end_time = time.time()

        # Snapshot memory usage after convex layer computation
        snapshot_after = tracemalloc.take_snapshot()

        # Take a snapshot of current memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        # Print peak memory usage and time
        print("\n_______________________________________________")
        print("Random generated points on a tested seed")
        print(f"Points volume: {points_in_list}")
        print(f"Peak Memory Usage: {peak / 1024:.2f} KB")
        print(f"Time taken to compute convex layers: {end_time - start_time:.4f} seconds")
        print(f"Layers computed: {len(convex_layers)}")

        if LET_ANIMATION:
        
            fig, ax = plt.subplots(figsize=(X_WINDOW, Y_WINDOW))
            ax.set_xlim(0, X_LIM)
            ax.set_ylim(0, Y_LIM)
            ax.set_title(TITLE_WINDOW)
            scat = ax.scatter(
                points[:, 0], 
                points[:, 1], 
                c=POINTS_COLOR, 
                s=POINT_SIZE,
                alpha=1.0, 
                label='Points'
            )
            line, = ax.plot([], [], 'r-', lw=LINE_SIZE, label='Current Convex Hull')

            alphas = np.ones(len(points))
            previous_hulls = []
            verified_hulls = []

            def init():
                line.set_data([], [])
                scat.set_alpha(alphas)
                return [scat, line] + previous_hulls + verified_hulls
            
            def animate(i):
                global alphas, previous_hulls, verified_hulls
                
                if i >= len(convex_layers):
                    return [scat, line] + previous_hulls + verified_hulls
                    
                layer = convex_layers[i]
                is_last_layer = (i == len(convex_layers) - 1)
                
                # Handle different cases based on number of points in layer
                if len(layer) >= 3:
                    # Normal convex hull - close the loop
                    x = np.append(layer[:, 0], layer[0, 0])
                    y = np.append(layer[:, 1], layer[0, 1])
                elif len(layer) == 2:
                    # Line segment - no need to close loop
                    x = layer[:, 0]
                    y = layer[:, 1]
                else:  # Single point
                    if is_last_layer:
                        # For last layer single point, make it visible as a point
                        line.set_data([], [])  # Clear the line
                        point_idx = np.where((points == layer[0]).all(axis=1))[0][0]
                        current_colors = np.array([POINTS_COLOR] * len(points))
                        current_colors[point_idx] = CURRENT_HULL_COLOR
                        scat.set_color(current_colors)
                        return [scat, line] + previous_hulls + verified_hulls
                    else:
                        # For non-last layer single points, use tiny line segment
                        x = np.array([layer[0, 0], layer[0, 0]])
                        y = np.array([layer[0, 1], layer[0, 1]])
                
                # Update the main line
                line.set_data(x, y)
                
                # Find indices of current hull points in the original dataset
                hull_indices = [np.where((points == point).all(axis=1))[0][0] for point in layer]
                
                if not is_last_layer:
                    # Not the last layer - fade previous hulls
                    for hull in previous_hulls:
                        hull.set_color(CHECKED_HULL_COLOR)
                        hull.set_alpha(0.4)
                        verified_hulls.append(hull)
                    previous_hulls.clear()
                    
                    # Add current hull to previous_hulls
                    hull_line, = ax.plot(x, y, CHECKED_HULL_COLOR, lw=1, alpha=0.6)
                    previous_hulls.append(hull_line)
                    
                    # Reduce opacity of points in this hull
                    for idx in hull_indices:
                        alphas[idx] *= 0.5
                else:
                    # Last layer - keep it distinct
                    if len(layer) > 1:  # Only create hull line if more than one point
                        hull_line, = ax.plot(x, y, CURRENT_HULL_COLOR, lw=2, alpha=1.0)
                        previous_hulls.append(hull_line)
                
                # Update scatter plot alphas
                scat.set_alpha(alphas)
                
                # Reset point colors to default (in case we had a red point before)
                scat.set_color(POINTS_COLOR)
                
                return [scat, line] + previous_hulls + verified_hulls

            # Create animation
            ani = FuncAnimation(
                fig, animate, 
                frames=len(convex_layers), 
                init_func=init, blit=True, 
                interval=ANIMATION_INTERVAL_MS, 
                repeat=False
            )

            # Save animation
            ani.save('convex_ani.gif',
                     writer='pillow',
                     fps=60)

            # Add legend
            ax.legend(
                handles=[
                    plt.Line2D([0], [0], color=CURRENT_HULL_COLOR, lw=2, label='Current Convex Hull'),
                    plt.Line2D([0], [0], color=CHECKED_HULL_COLOR, lw=2, label='Verified Hulls'),
                    plt.Line2D([0], [0], color=POINTS_COLOR, marker='o', linestyle='', label='Points'),
                    plt.Line2D([0], [0], color=CHECKED_POINTS_COLOR, marker='o', linestyle='', label='Verified Points')
                ],
                loc='upper right'
            )

            plt.tight_layout()
            plt.show()
