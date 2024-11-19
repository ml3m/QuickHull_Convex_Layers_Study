import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Step 1: Generate random 2D points
np.random.seed(42)  # For reproducibility
num_points = 10
points = np.random.rand(num_points, 2) * 100  # Scale points to a 100x100 grid


# Step 2: Function to compute convex layers
def compute_convex_layers(points):
    layers = []
    remaining_points = points.copy()

    while len(remaining_points) > 2:
        hull = ConvexHull(remaining_points)
        layers.append(remaining_points[hull.vertices])  # Save current hull points
        remaining_points = np.delete(remaining_points, hull.vertices, axis=0)  # Remove hull points

    return layers


convex_layers = compute_convex_layers(points)

# Step 3: Animation setup
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.set_title("Convex Layers Animation")
scat = ax.scatter(points[:, 0], points[:, 1], c='black', alpha=1.0, label='Points')
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

        # Move previous hulls to verified hulls and fade them
        for hull in previous_hulls:
            hull.set_color('blue')
            hull.set_alpha(0.4)
            verified_hulls.append(hull)
        previous_hulls.clear()

        # Save the current hull to the previous hulls list
        hull_line, = ax.plot(x, y, 'gray', lw=1, alpha=0.6)  # Add new faded hull
        previous_hulls.append(hull_line)

        # Find indices of current hull points in the original dataset
        hull_indices = [np.where((points == point).all(axis=1))[0][0] for point in layer]

        # Reduce opacity of these points
        for idx in hull_indices:
            alphas[idx] *= 0.5  # Reduce alpha by 50% (or set to a fixed lower value)

        # Update scatter plot
        scat.set_alpha(alphas)

    # Return all artists to ensure they are redrawn
    return [scat, line] + previous_hulls + verified_hulls


# Create animation
ani = FuncAnimation(
        fig, animate, frames=len(convex_layers), 
        init_func=init, blit=True, interval=300, repeat=False)

# Add updated legend
ax.legend(
    handles=[
        plt.Line2D([0], [0], color='r', lw=2, label='Current Convex Hull'),
        plt.Line2D([0], [0], color='blue', lw=2, label='Verified Hulls'),
        plt.Line2D([0], [0], color='gray', lw=1, label='Faded Hulls'),
        plt.Line2D([0], [0], color='black', marker='o', linestyle='', label='Points')
    ],
    loc='upper right'  # Place the legend in the upper-right corner
)

# Show animation
plt.show()
