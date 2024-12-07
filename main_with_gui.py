import matplotlib
matplotlib.use('MacOSX')  # Try this before importing pyplot

import os
os.environ['TK_LIBRARY'] = '/opt/homebrew/opt/tcl-tk/lib/tk8.6'
os.environ['TCL_LIBRARY'] = '/opt/homebrew/opt/tcl-tk/lib/tcl8.6'

import tkinter as tk
from tkinter import ttk
import numpy as np
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tracemalloc
import sys
sys.path.append('.')  # Add current directory to python path


# Import from existing project files
from convexhull_quickhull_implementation import ConvexHull_QuickHull as ConvexHull
import config

class ConvexHullVisualizationApp:
    def __init__(self, master):
        self.master = master
        master.title("Convex Hull Visualization")
        master.geometry("600x500")

        # Create configuration frame
        config_frame = ttk.LabelFrame(master, text="Visualization Settings")
        config_frame.pack(padx=10, pady=10, fill='x')

        # Points Count
        ttk.Label(config_frame, text="Points Count:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.points_var = tk.StringVar(value="250")
        points_entry = ttk.Entry(config_frame, textvariable=self.points_var, width=10)
        points_entry.grid(row=0, column=1, padx=5, pady=5)

        # Animation Speed
        ttk.Label(config_frame, text="Animation Interval (ms):").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.interval_var = tk.StringVar(value="300")
        interval_entry = ttk.Entry(config_frame, textvariable=self.interval_var, width=10)
        interval_entry.grid(row=1, column=1, padx=5, pady=5)

        # Random Seed
        ttk.Label(config_frame, text="Random Seed:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.seed_var = tk.StringVar(value="1330")
        seed_entry = ttk.Entry(config_frame, textvariable=self.seed_var, width=10)
        seed_entry.grid(row=2, column=1, padx=5, pady=5)

        # Visualization Button
        start_button = ttk.Button(config_frame, text="Start Visualization", command=self.start_visualization)
        start_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        # Matplotlib Figure Frame (initially empty)
        self.fig_frame = ttk.Frame(master)
        self.fig_frame.pack(padx=10, pady=10, fill='both', expand=True)

    def start_visualization(self):
        # Clear previous figure frame if exists
        for widget in self.fig_frame.winfo_children():
            widget.destroy()

        # Parse inputs
        points_count = int(self.points_var.get())
        animation_interval = int(self.interval_var.get())
        random_seed = int(self.seed_var.get())

        # Update config dynamically
        config.POINTS_LIST = [points_count]
        config.ANIMATION_INTERVAL_MS = animation_interval
        config.RANDOM_SEED = random_seed
        config.TITLE_WINDOW = f"Convex Layers Animation: {animation_interval}ms with {points_count} points and seed: {random_seed}"

        # Set random seed if needed
        if not config.PERMIT_RANDOM_SEED:
            np.random.seed(random_seed)

        # Generate random points
        points = np.random.rand(points_count, 2) * config.POINTS_RANGE

        # Create figure and matplotlib canvas
        fig, ax = plt.subplots(figsize=(config.X_WINDOW, config.Y_WINDOW))
        canvas = FigureCanvasTkAgg(fig, master=self.fig_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill='both', expand=True)

        # Existing matplotlib setup from main.py
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

        # Compute convex layers (existing function)
        def compute_convex_layers(points):
            layers = []
            remaining_points = points.copy()
            
            while len(remaining_points) > 0:
                if len(remaining_points) >= 3:
                    hull = ConvexHull(remaining_points)
                    layers.append(remaining_points[hull.vertices])
                    remaining_points = np.delete(remaining_points, hull.vertices, axis=0)
                else:
                    # Handle cases with 1 or 2 points
                    if len(remaining_points) == 2:
                        layers.append(remaining_points)
                    elif len(remaining_points) == 1:
                        layers.append(remaining_points)
                    remaining_points = np.array([])
                
            return layers

        # Animation setup
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

        # Performance logging
        snapshot_after = tracemalloc.take_snapshot()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        print("\n_______________________________________________")
        print(f"Points volume: {points_count}")
        print(f"Peak Memory Usage: {peak / 1024:.2f} KB")
        print(f"Time taken to compute convex layers: {end_time - start_time:.4f} seconds")
        print(f"Layers computed: {len(convex_layers)}")

        # Create animation
        ani = FuncAnimation(
            fig, animate, 
            frames=len(convex_layers), 
            init_func=init, 
            blit=True, 
            interval=animation_interval, 
            repeat=False
        )

        # Add legend
        ax.legend(
            handles=[
                plt.Line2D([0], [0], color=config.CURRENT_HULL_COLOR, lw=2, label='Current Convex Hull'),
                plt.Line2D([0], [0], color=config.CHECKED_HULL_COLOR, lw=2, label='Verified Hulls'),
                plt.Line2D([0], [0], color=config.POINTS_COLOR, marker='o', linestyle='', label='Points'),
                plt.Line2D([0], [0], color=config.CHECKED_POINTS_COLOR, marker='o', linestyle='', label='Verified Points')
            ],
            loc='upper right'
        )

        plt.tight_layout()
        canvas.draw()

def main():
    root = tk.Tk()
    app = ConvexHullVisualizationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
