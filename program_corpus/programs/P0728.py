def traffic_step(road, vmax=3):
    length = len(road)
    new_road = [-1] * length
    for pos in range(length):
        speed = road[pos]
        if speed < 0:
            continue
        gap = 0
        while gap < vmax and road[(pos + gap + 1) % length] < 0 and gap < length - 1:
            gap += 1
        new_speed = min(speed + 1, vmax, gap)
        new_road[(pos + new_speed) % length] = new_speed
    return new_road

def run_traffic(road, steps, vmax=3):
    flows = []
    for _ in range(steps):
        road = traffic_step(road, vmax)
        flows.append(sum(v for v in road if v >= 0) / max(sum(1 for v in road if v >= 0), 1))
    return road, flows

if __name__ == "__main__":
    road = [0, -1, -1, 0, -1, -1]
    final, flows = run_traffic(road, 2, 2)
    assert final == [2, -1, -1, 2, -1, -1]
    assert flows == [1.0, 2.0]
