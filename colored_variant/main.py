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
    
def generate_distinct_colors(n):
    """
    Generate n visually distinct colors using HSV color space.
    """
    colors = []
    for i in range(n):
        hue = i / n
        saturation = 0.7 + np.random.random() * 0.3  # Random between 0.7-1.0
        value = 0.7 + np.random.random() * 0.3       # Random between 0.7-1.0
        rgb = plt.cm.hsv(hue)[:3]  # Convert HSV to RGB
        colors.append(rgb)
    return colors

def generate_grid_points(grid_size, x_range, y_range):
    """
    Generate points in a grid format based on the specified grid size and ranges.
    
    Args:
        grid_size (int): Number of points along one axis of the grid.
        x_range (float): Maximum value for the x-coordinate.
        y_range (float): Maximum value for the y-coordinate.
    
    Returns:
        np.ndarray: Array of generated points in a grid.
    """
    x_values = np.linspace(0, x_range, grid_size)
    y_values = np.linspace(0, y_range, grid_size)
    
    # Create a meshgrid of points
    x_grid, y_grid = np.meshgrid(x_values, y_values)
    
    # Stack x and y coordinates into a single array of points
    points = np.vstack([x_grid.ravel(), y_grid.ravel()]).T
    return points

def compute_convex_layers(points):
    layers = []
    remaining_points = points.copy()
    used_indices = set()
    
    while len(remaining_points) > 0:
        if len(remaining_points) >= 3:
            hull = ConvexHull(remaining_points)
            hull_points = remaining_points[hull.vertices]
            layers.append(hull_points)
            
            # Remove hull points from remaining points
            mask = np.ones(len(remaining_points), dtype=bool)
            mask[hull.vertices] = False
            remaining_points = remaining_points[mask]
        else:
            layers.append(remaining_points)
            remaining_points = np.array([])
    
    return layers

def generate_collinear_points(n, x_range=1000):
    """
    Generate n collinear points along the x-axis (y = 0).
    
    Args:
        n (int): Number of points to generate.
        x_range (float): The range of x-values for the points.
    
    Returns:
        np.ndarray: Array of n collinear points along the x-axis.
    """
    x = np.linspace(0, x_range, n)
    y = np.linspace(500, 500, n)  # All y values are 0, hence collinear
    return np.vstack([x, y]).T


#def init():
#    line.set_data([], [])
#    scat.set_alpha(alphas)
#    return [scat, line] + previous_hulls + verified_hulls

def init():
    line.set_data([], [])
    scat.set_alpha(alphas)
    return [scat, line] + hull_lines

def animate(i):
    global alphas, hull_lines
    
    if i >= len(convex_layers):
        return [scat, line] + hull_lines
        
    layer = convex_layers[i]
    is_last_layer = (i == len(convex_layers) - 1)
    
    # Handle different cases based on number of points in layer
    if len(layer) >= 3:
        x = np.append(layer[:, 0], layer[0, 0])
        y = np.append(layer[:, 1], layer[0, 1])
    elif len(layer) == 2:
        x = layer[:, 0]
        y = layer[:, 1]
    else:  # Single point
        if is_last_layer:
            line.set_data([], [])
            point_idx = np.where((points == layer[0]).all(axis=1))[0][0]
            # Convert colors to RGB tuples
            current_colors = np.array([plt.cm.colors.to_rgb(POINTS_COLOR)] * len(points))
            current_colors[point_idx] = layer_colors[i]
            scat.set_color(current_colors)
            return [scat, line] + hull_lines
        else:
            x = np.array([layer[0, 0], layer[0, 0]])
            y = np.array([layer[0, 1], layer[0, 1]])
    
    # Update the main line
    line.set_data(x, y)
    
    # Find indices of current hull points
    hull_indices = [np.where((points == point).all(axis=1))[0][0] for point in layer]
    
    # Create or update hull line with the corresponding color
    if len(layer) > 1:
        hull_line, = ax.plot(x, y, color=layer_colors[i], lw=CHECKED_LINE_SIZE, alpha=1.0)
        hull_lines.append(hull_line)
    
    # Update scatter plot colors
    scat.set_color(POINTS_COLOR)
    
    return [scat, line] + hull_lines

for points_in_list in POINTS_LIST:

############## types of generation ##############

    #points = np.random.rand(points_in_list, 2) * POINTS_RANGE

    # Generate points in a grid format

    #grid_size = int(np.sqrt(points_in_list))  # Estimate grid size for the given number of points
    #points = generate_grid_points(grid_size, POINTS_RANGE, POINTS_RANGE)
    #points = np.random.rand(points_in_list, 2) * POINTS_RANGE
    points = generate_collinear_points(30)


            # Animation setup
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
    line, = ax.plot([], [], 'r-', lw=CHECKED_LINE_SIZE, label='Current Convex Hull')

    alphas = np.ones(len(points))
    previous_hulls = []
    verified_hulls = []


    tracemalloc.start()

    convex_layers = compute_convex_layers(points)

    layer_colors = generate_distinct_colors(len(convex_layers))
    
    # Animation setup
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
    line, = ax.plot([], [], 'r-', lw=LINE_SIZE, label='Current Layer')
    
    alphas = np.ones(len(points))
    hull_lines = []
    
    if LET_ANIMATION:
        ani = FuncAnimation(
            fig, animate, 
            frames=len(convex_layers), 
            init_func=init, blit=True, 
            interval=ANIMATION_INTERVAL_MS, 
            repeat=False
        )
        
    # Save the animation as GIF
    ani.save(f"layers.gif", writer='pillow')
    
    plt.tight_layout()
    plt.show()
