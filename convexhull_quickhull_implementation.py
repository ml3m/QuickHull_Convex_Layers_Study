import numpy as np

class ConvexHull_QuickHull:
    def __init__(self, points):
        """
        Compute the convex hull using QuickHull algorithm.
        
        Parameters:
        points (numpy.ndarray): Array of points with shape (n, 2)
        """
        self.points = np.asarray(points)
        self.vertices = self._quickhull()
        self._compute_additional_properties()
    
    def _line_side(self, point, line_start, line_end):
        """
        Determine which side of a line a point is on.
        Returns positive value if point is on left side,
        negative if on right side, zero if on the line.
        """
        return ((line_end[0] - line_start[0]) * (point[1] - line_start[1]) - 
                (line_end[1] - line_start[1]) * (point[0] - line_start[0]))
    
    def _find_hull(self, points, p1, p2, side):
        """
        Recursive function to find points in the convex hull.
        
        Parameters:
        points (array): Set of points to check
        p1, p2: Two points defining the line
        side: Side to search for points
        
        Returns list of points in the convex hull
        """
        if len(points) == 0:
            return []
        
        # Find point furthest from the line
        max_dist = 0
        max_point_idx = -1
        for i, point in enumerate(points):
            dist = abs(self._line_side(point, p1, p2))
            if dist > max_dist:
                max_dist = dist
                max_point_idx = i
        
        if max_point_idx == -1:
            return []
        
        max_point = points[max_point_idx]
        
        # Recursively find points on the left and right side of lines
        # formed by max_point and the original line endpoints
        points_left_1 = [p for p in points if self._line_side(p, p1, max_point) > 0]
        points_left_2 = [p for p in points if self._line_side(p, max_point, p2) > 0]
        
        hull_1 = self._find_hull(points_left_1, p1, max_point, side)
        hull_2 = self._find_hull(points_left_2, max_point, p2, side)
        
        return hull_1 + [max_point] + hull_2
    
    def _quickhull(self):
        """
        Main QuickHull algorithm implementation.
        
        Returns array of vertex indices
        """
        # Find leftmost and rightmost points
        left_point = self.points[np.argmin(self.points[:, 0])]
        right_point = self.points[np.argmax(self.points[:, 0])]
        
        # Divide points into two sets
        points_above = [p for p in self.points if self._line_side(p, left_point, right_point) > 0]
        points_below = [p for p in self.points if self._line_side(p, left_point, right_point) < 0]
        
        # Find hull points
        hull_above = self._find_hull(points_above, left_point, right_point, 1)
        hull_below = self._find_hull(points_below, right_point, left_point, -1)
        
        # Combine and find indices
        hull_points = [left_point] + hull_above + [right_point] + hull_below
        
        # Remove duplicates while preserving order
        unique_hull_points = []
        for point in hull_points:
            # Use numpy's array comparison to check for duplicates
            if not any(np.array_equal(point, existing) for existing in unique_hull_points):
                unique_hull_points.append(point)
        
        # Convert back to indices
        hull_indices = [np.where((self.points == point).all(axis=1))[0][0] for point in unique_hull_points]
        
        return np.array(hull_indices)
    
    def _compute_additional_properties(self):
        """
        Compute additional properties similar to scipy's ConvexHull
        """
        # Simplices (edges of the convex hull)
        n = len(self.vertices)
        self.simplices = np.column_stack([
            self.vertices, 
            np.roll(self.vertices, -1)
        ])
        
        # Area calculation using shoelace formula
        x = self.points[self.vertices, 0]
        y = self.points[self.vertices, 1]
        self.area = 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))
        
    def __len__(self):
        """Return number of vertices in convex hull"""
        return len(self.vertices)
