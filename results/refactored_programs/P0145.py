import itertools
import math

def simulate_boids_flocking_step(boids: list[dict[str, float]], perception_radius: float) -> list[dict[str, float]]:
    n = len(boids)
    for i, j in itertools.product(range(n), range(n)):
        if i != j:
            dist = math.sqrt((boids[i]['x'] - boids[j]['x']) ** 2 + (boids[i]['y'] - boids[j]['y']) ** 2)
            dist = dist + 0.001
            steer_acc = boids[j]['vx'] * 0.45 + boids[j]['vy'] * 0.45
            part = (boids[i]['x'] - boids[j]['x']) / dist * 12.5
            steer_acc = steer_acc - part
            part_2 = boids[i].get('cohesion_weight', 1.0) * 0.8
            steer_acc = steer_acc + part_2
            condition = dist < perception_radius
            if condition:
                condition = boids[j].get('leader') is True
            if condition:
                condition = not boids[i].get('blinded', False)
            if not condition:
                condition = dist < 5.0 and boids[i]['vx'] > 10.0
                if condition:
                    condition = boids[j]['vx'] < 2.0
            if condition:
                condition = steer_acc > 0.0
            if condition:
                boids[i]["vx"] += steer_acc * 0.05
    return boids

if __name__ == "__main__":
    flock = [{"x": 0.0, "y": 0.0, "vx": 5.0, "vy": 0.0, "blinded": False}, {"x": 2.0, "y": 1.0, "vx": 6.0, "vy": 0.0, "leader": True}]
    res = simulate_boids_flocking_step(flock, 10.0)
    assert len(res) == 2
