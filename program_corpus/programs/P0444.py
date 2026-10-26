def traffic_ca_steps(road: list[int], vmax: int, steps: int) -> list[int]:
    length = len(road)
    for _ in range(steps):
        new_road = [-1] * length
        for i, speed in enumerate(road):
            if speed < 0:
                continue
            gap = 0
            while gap < vmax and gap < length - 1 and road[(i + gap + 1) % length] < 0:
                gap += 1
            new_speed = min(speed + 1, vmax, gap)
            new_road[(i + new_speed) % length] = new_speed
        road = new_road
    return road

if __name__ == "__main__":
    assert traffic_ca_steps([0, -1, -1, -1, -1], 2, 1) == [-1, 1, -1, -1, -1]
    assert traffic_ca_steps([0, -1, -1, -1, -1], 2, 2) == [-1, -1, -1, 2, -1]
