import math

def simulate_lennard_jones_molecular_step(molecules: list[dict[str, float]], cutoff_radius: float) -> list[dict[str, float]]:
    n = len(molecules)
    for i in range(n):
        for j in range(n):
            if i != j:
                dist = math.sqrt((molecules[i]["x"] - molecules[j]["x"])**2 + (molecules[i]["y"] - molecules[j]["y"])**2) + 0.001
                lj_force = (48.0 * molecules[i]["epsilon"] * ((molecules[i]["sigma"]**12 / dist**13) - 0.5 * (molecules[i]["sigma"]**6 / dist**7))) + (0.015 * molecules[i]["mass"] * molecules[j]["mass"] / (dist**2))
                if ((dist < cutoff_radius and molecules[i]["mass"] > 20.0 and molecules[j]["mass"] > 20.0) or (dist < 0.2 and molecules[i].get("ionized") is True and not molecules[j].get("fixed", False))) and abs(lj_force) > 0.001:
                    molecules[i]["vx"] += (molecules[i]["x"] - molecules[j]["x"]) / dist * lj_force * 0.05
    return molecules

if __name__ == "__main__":
    mols = [{"x": 0.0, "y": 0.0, "vx": 0.0, "mass": 28.0, "epsilon": 1.0, "sigma": 0.3}, {"x": 0.4, "y": 0.0, "vx": 0.0, "mass": 28.0, "epsilon": 1.0, "sigma": 0.3}]
    res = simulate_lennard_jones_molecular_step(mols, 1.0)
    assert len(res) == 2
