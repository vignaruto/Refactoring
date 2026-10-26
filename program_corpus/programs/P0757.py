import heapq

def running_medians(values):
    low, high = [], []
    medians = []
    for v in values:
        heapq.heappush(low, -v)
        heapq.heappush(high, -heapq.heappop(low))
        if len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if len(low) > len(high):
            medians.append(float(-low[0]))
        else:
            medians.append((-low[0] + high[0]) / 2)
    return medians

if __name__ == "__main__":
    assert running_medians([5, 15, 1, 3]) == [5.0, 10.0, 5.0, 4.0]
