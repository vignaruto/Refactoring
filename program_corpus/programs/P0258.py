from collections import deque

def round_robin_completion(bursts: dict[str, int], quantum: int) -> dict[str, int]:
    queue = deque(bursts.items())
    clock = 0
    finished: dict[str, int] = {}
    while queue:
        name, remaining = queue.popleft()
        run = min(quantum, remaining)
        clock += run
        if remaining > run:
            queue.append((name, remaining - run))
        else:
            finished[name] = clock
    return finished

if __name__ == "__main__":
    assert round_robin_completion({"A": 5, "B": 2, "C": 4}, 2) == {"B": 4, "C": 10, "A": 11}
