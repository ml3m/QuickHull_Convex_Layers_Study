import numpy as np
import time
import matplotlib.pyplot as plt

from matplotlib.animation import FuncAnimation
from convexhull_quickhull_implementation import ConvexHull_QuickHull as ConvexHull

# Step 1: Generate random 2D points
PERMIT_1_OR_2_REMAINING_POINTS = True
PERMIT_RANDOM_SEED = False
REMAINING_POINTS_COMPUTE_CH = 1
RANDOM_SEED = 1330
NUMBER_POINTS = 51
ANIMATION_INTERVAL_MS = 200
X_LIM = 1000
Y_LIM = 1000
X_WINDOW = 10
Y_WINDOW = 10
POINTS_RANGE = 1000

CHECKED_HULL_COLOR = 'gray'
CURRENT_HULL_COLOR = 'red'
POINTS_COLOR = 'black'

# For reproducibility
if not PERMIT_RANDOM_SEED:
    np.random.seed(RANDOM_SEED)  

points = np.random.rand(NUMBER_POINTS, 2) * POINTS_RANGE  # Scale points to a 100x100 grid

# Step 2: Function to compute convex layers
def compute_convex_layers(points):
    layers = []
    remaining_points = points.copy()

    while len(remaining_points) > REMAINING_POINTS_COMPUTE_CH:
        hull = ConvexHull(remaining_points)
        layers.append(remaining_points[hull.vertices])  # Save current hull points
        remaining_points = np.delete(remaining_points, hull.vertices, axis=0)  # Remove hull points
        
        ## If there are fewer than 3 points left, stop
        if len(remaining_points) <= REMAINING_POINTS_COMPUTE_CH and PERMIT_1_OR_2_REMAINING_POINTS:
            break

    return layers


# Measure the time to compute convex layers
start_time = time.time()
convex_layers = compute_convex_layers(points)
end_time = time.time()
print(f"Time taken to compute convex layers: {end_time - start_time:.4f} seconds")


# Step 3: Animation setup
fig, ax = plt.subplots(figsize=(X_WINDOW, Y_WINDOW))
ax.set_xlim(0, X_LIM)
ax.set_ylim(0, Y_LIM)
ax.set_title("Convex Layers Animation")
scat = ax.scatter(points[:, 0], points[:, 1], c=POINTS_COLOR, alpha=1.0, label='Points')
line, = ax.plot([], [], 'r-', lw=2, label='Current Convex Hull')


# Create an array to track opacity for each point
alphas = np.ones(len(points))

# Lists to store hulls
previous_hulls = []  # Line2D objects for faded hulls
verified_hulls = []  # Line2D objects for verified hulls


# Initialize animation
def init():
    line.set_data([], [])
    scat.set_alpha(alphas)
    return [scat, line] + previous_hulls + verified_hulls


# Animation function
def animate(i):
    global alphas, previous_hulls, verified_hulls

    if i < len(convex_layers):
        layer = convex_layers[i]
        # Update line for current convex hull
        x, y = np.append(layer[:, 0], layer[0, 0]), np.append(layer[:, 1], layer[0, 1])  # Close the hull loop
        line.set_data(x, y)

        # If this is not the last hull, treat it as a verified hull
        if i < len(convex_layers) - 1:
            # Move previous hulls to verified hulls and fade them
            for hull in previous_hulls:
                hull.set_color(CHECKED_HULL_COLOR)
                hull.set_alpha(0.4)
                verified_hulls.append(hull)
            previous_hulls.clear()

            # Save the current hull to the previous hulls list
            hull_line, = ax.plot(x, y, CHECKED_HULL_COLOR, lw=1, alpha=0.6)  # Add new faded hull
            previous_hulls.append(hull_line)
        else:
            # Special handling for the last hull
            hull_line, = ax.plot(x, y, CURRENT_HULL_COLOR, lw=2, alpha=1.0)  # Keep distinct style for last hull

        # Find indices of current hull points in the original dataset
        hull_indices = [np.where((points == point).all(axis=1))[0][0] for point in layer]

        # Reduce opacity of these points only if this is not the last hull
        if i < len(convex_layers) - 1:
            for idx in hull_indices:
                alphas[idx] *= 0.5  # Reduce alpha by 50% (or set to a fixed lower value)

        # Update scatter plot
        scat.set_alpha(alphas)

    # Return all artists to ensure they are redrawn
    return [scat, line] + previous_hulls + verified_hulls


# Create animation
ani = FuncAnimation(
        fig, animate, 
        frames=len(convex_layers), 
        init_func=init, blit=True, 
        interval=ANIMATION_INTERVAL_MS, 
        repeat=False
        )

# Add updated legend
ax.legend(
    handles=[
        plt.Line2D([0], [0], color=CURRENT_HULL_COLOR, lw=2, label='Current Convex Hull'),
        plt.Line2D([0], [0], color=CHECKED_HULL_COLOR, lw=2, label='Verified Hulls'),
        plt.Line2D([0], [0], color=POINTS_COLOR, marker='o', linestyle='', label='Points')
    ],
    loc='upper right'  # Place the legend in the upper-right corner
)

# Show animation
plt.show()
