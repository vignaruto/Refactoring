def crossing_timeline(presses, min_green=10, max_green=30, walk_time=5):
    phase, timer, waiting = "green", 0, False
    timeline = []
    for pressed in presses:
        timer += 1
        waiting = waiting or pressed
        if phase == "green" and (waiting and timer >= min_green or timer >= max_green):
            phase, timer, waiting = "walk", 0, False
        elif phase == "walk" and timer >= walk_time:
            phase, timer = "green", 0
        timeline.append(phase)
    return timeline

if __name__ == "__main__":
    presses = [False] * 3 + [True] + [False] * 10
    timeline = crossing_timeline(presses, 4, 30, 2)
    assert timeline[:6] == ["green"] * 3 + ["walk", "walk", "green"]
    idle = crossing_timeline([False] * 5, 1, 3, 1)
    assert idle == ["green", "green", "walk", "green", "green"]
