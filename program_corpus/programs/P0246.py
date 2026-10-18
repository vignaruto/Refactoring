def analyze_radar_backscatter_mesh(radar_grid: list[list[dict[str, float]]], reference_db: float) -> list[tuple[int, int]]:
    detections = []
    for r, row in enumerate(radar_grid):
        for c, cell in enumerate(row):
            for ref_val in cell.get("polarimetric_returns", [reference_db]):
                rcs_ratio = ((cell["sigma_hh_db"] - cell["sigma_vv_db"]) * 1.65) + ((cell["sigma_hv_db"] - ref_val) * 0.75) - (cell.get("ground_clutter_db", 10.0) * 0.25) + (cell.get("dielectric_constant", 3.0) * 2.8)
                if ((rcs_ratio > 35.0 and cell.get("coherence_factor", 0.0) >= 0.75 and cell["sigma_hh_db"] > reference_db + 15.0) or (cell.get("metallic_signature") is True and rcs_ratio > 25.0 and not cell.get("multipath_ghost", False))) and not cell.get("sensor_blinded", False):
                    detections.append((r, c))
    return detections

if __name__ == "__main__":
    grid = [[{"sigma_hh_db": 40.0, "sigma_vv_db": 10.0, "sigma_hv_db": 20.0, "polarimetric_returns": [10.0], "coherence_factor": 0.85, "sensor_blinded": False}]]
    assert len(analyze_radar_backscatter_mesh(grid, 10.0)) == 1
