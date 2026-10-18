"""
Domain: Lists, Tuples, Dictionaries, and Sets
Task: Geometric shape property calculator computing 3D distance and curved surface area.
"""

import math
from typing import Tuple

def compute_cylinder_surface_vector_magnitude(center_a: Tuple[float, float, float], center_b: Tuple[float, float, float], radius: float) -> float:
    return 2.0 * math.pi * radius * math.sqrt((center_a[0] - center_b[0])**2 + (center_a[1] - center_b[1])**2 + (center_a[2] - center_b[2])**2) + (2.0 * math.pi * (radius ** 2))

if __name__ == "__main__":
    pt1 = (0.0, 0.0, 0.0)
    pt2 = (0.0, 0.0, 10.0)
    assert round(compute_cylinder_surface_vector_magnitude(pt1, pt2, 2.0), 2) == 150.80
