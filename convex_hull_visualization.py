import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import tracemalloc
from convexhull_quickhull_implementation import ConvexHull_QuickHull as ConvexHull
import config

def generate_points(points_in_list):
    """
    Generate random points based on configuration
    """
    # For reproducibility
    if not config.PERMIT_RANDOM_SEED:
        np.random.seed(config.RANDOM_SEED)  

    # Generate points within the specified range
    points = np.random.rand(points_in_list, 2) * config.POINTS_RANGE
    return points

def compute_convex_layers(points):
    """
    Compute convex hull layers with optional 1-2 point handling
    """
    layers = []
    remaining_points = points.copy()
    
    while len(remaining_points) > 0:
        if len(remaining_points) >= 3:
            # Normal convex hull computation for 3 or more points
            hull = ConvexHull(remaining_points)
            layers.append(remaining_points[hull.vertices])
            remaining_points = np.delete(remaining_points, hull.vertices, axis=0)
        else:
            # Handle cases with 1 or 2 points based on configuration
            if config.PERMIT_1_OR_2_REMAINING_POINTS:
                if len(remaining_points) == 2:
                    # For 2 points, create a degenerate hull (line)
                    layers.append(remaining_points)
                elif len(remaining_points) == 1:
                    # For 1 point, add it as a single-point layer
                    layers.append(remaining_points)
            remaining_points = np.array([])  # Clear remaining points
            
    return layers

def create_animation(points):
    """
    Create and display the convex hull layers animation
    """
    # Animation setup
    fig, ax = plt.subplots(figsize=(config.X_WINDOW, config.Y_WINDOW))
    ax.set_xlim(0, config.X_LIM)
    ax.set_ylim(0, config.Y_LIM)
    ax.set_title(config.TITLE_WINDOW)
    
    scat = ax.scatter(
        points[:, 0], 
        points[:, 1], 
        c=config.POINTS_COLOR, 
        s=config.POINT_SIZE,
        alpha=1.0, 
        label='Points'
    )
    line, = ax.plot([], [], 'r-', lw=config.LINE_SIZE, label='Current Convex Hull')

    alphas = np.ones(len(points))
    previous_hulls = []
    verified_hulls = []

    def init():
        line.set_data([], [])
        scat.set_alpha(alphas)
        return [scat, line] + previous_hulls + verified_hulls

    def animate(i):
        nonlocal alphas, previous_hulls, verified_hulls
        
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
                # Find the index of this point in the original dataset
                point_idx = np.where((points == layer[0]).all(axis=1))[0][0]
                # Update the scatter plot to show this point in red
                current_colors = np.array([config.POINTS_COLOR] * len(points))
                current_colors[point_idx] = config.CURRENT_HULL_COLOR
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
                hull.set_color(config.CHECKED_HULL_COLOR)
                hull.set_alpha(0.4)
                verified_hulls.append(hull)
            previous_hulls.clear()
            
            # Add current hull to previous_hulls
            hull_line, = ax.plot(x, y, config.CHECKED_HULL_COLOR, lw=1, alpha=0.6)
            previous_hulls.append(hull_line)
            
            # Reduce opacity of points in this hull
            for idx in hull_indices:
                alphas[idx] *= 0.5
        else:
            # Last layer - keep it distinct
            if len(layer) > 1:  # Only create hull line if more than one point
                hull_line, = ax.plot(x, y, config.CURRENT_HULL_COLOR, lw=2, alpha=1.0)
                previous_hulls.append(hull_line)
        
        # Update scatter plot alphas
        scat.set_alpha(alphas)
        
        # Reset point colors to default (in case we had a red point before)
        scat.set_color(config.POINTS_COLOR)
        
        return [scat, line] + previous_hulls + verified_hulls

    # Compute convex layers
    tracemalloc.start()
    start_time = time.time()
    convex_layers = compute_convex_layers(points)
    end_time = time.time()
    snapshot_after = tracemalloc.take_snapshot()

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Print performance metrics
    print("\n_______________________________________________")
    print("Random generated points")
    print(f"Points volume: {len(points)}")
    print(f"Peak Memory Usage: {peak / 1024:.2f} KB")
    print(f"Time taken to compute convex layers: {end_time - start_time:.
