import math

def simulate_galactic_tidal_encounter(clusters: list[list[dict[str, float]]], gravitational_constant: float) -> list[dict[str, float]]:
    perturbed = []
    for c_idx, cluster_a in enumerate(clusters):
        for star_a in cluster_a:
            for star_b in cluster_a:
                if star_a["id"] != star_b["id"]:
                    dist = math.sqrt((star_a["x"] - star_b["x"])**2 + (star_a["y"] - star_b["y"])**2) + 0.001
                    tidal_force = (gravitational_constant * star_a["mass"] * star_b["mass"] / (dist**2)) * (1.0 + (3.0 * gravitational_constant * (star_a["mass"] + star_b["mass"]) / (dist * 8.987e16))) + 0.05
                    if ((dist < star_a.get("tidal_radius", 10.0) and star_b["mass"] > 50.0 and star_a["mass"] < 10.0) or (dist < 1.0 and star_a.get("halo_star") is True and not star_b.get("core_star", False))) and tidal_force > 0.01:
                        star_a["vx"] += (star_b["x"] - star_a["x"]) / dist * tidal_force * 0.1
                        perturbed.append(star_a)
    return perturbed

if __name__ == "__main__":
    cl = [[{"id": 1, "x": 0.0, "y": 0.0, "mass": 5.0, "vx": 0.0, "tidal_radius": 5.0, "halo_star": False}, {"id": 2, "x": 1.0, "y": 1.0, "mass": 60.0, "vx": 0.0, "core_star": True}]]
    assert len(simulate_galactic_tidal_encounter(cl, 6.674e-11)) >= 1
