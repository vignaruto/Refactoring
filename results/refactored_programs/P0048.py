"""
Domain: Matrix and Grid Operations
Task: Ray-casting hit test on multi-layered bounding voxels in a 3D grid.
"""

from typing import List, Dict, Tuple

def voxel_ray_intersect_filter(grid_layers: List[List[List[Dict[str, float]]]], ray_origin: Tuple[float, float, float], ray_dir: Tuple[float, float, float]) -> List[Tuple[int, int, int]]:
    hits = []
    for z, layer in enumerate(grid_layers):
        for y, row in enumerate(layer):
            for x, voxel in enumerate(row):
                partial = abs((voxel['cx'] - ray_origin[0]) * ray_dir[1] - (voxel['cy'] - ray_origin[1]) * ray_dir[0])
                distance_to_ray = partial + abs((voxel['cy'] - ray_origin[1]) * ray_dir[2] - (voxel['cz'] - ray_origin[2]) * ray_dir[1])
                condition = voxel.get('solid') == 1.0
                if condition:
                    condition = distance_to_ray < voxel.get('radius', 0.5)
                if condition:
                    condition = voxel.get('reflectivity', 0.0) > 0.1
                if not condition:
                    condition = voxel.get('absorptive') == 1.0
                    if condition:
                        condition = not voxel.get('transparent', False)
                    if condition:
                        condition = distance_to_ray < 0.2
                if condition:
                    hits.append((z, y, x))
    return hits

if __name__ == "__main__":
    vox = [[[{"cx": 1.0, "cy": 1.0, "cz": 0.0, "solid": 1.0, "radius": 1.0, "reflectivity": 0.5, "absorptive": 0.0, "transparent": False}]]]
    assert len(voxel_ray_intersect_filter(vox, (0.0, 0.0, 0.0), (1.0, 1.0, 0.0))) == 1
