import heapq

def min_meeting_rooms(intervals: list[tuple[int, int]]) -> int:
    ends: list[int] = []
    for start, end in sorted(intervals):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)

if __name__ == "__main__":
    assert min_meeting_rooms([(0, 30), (5, 10), (15, 20)]) == 2
    assert min_meeting_rooms([(1, 2), (2, 3)]) == 1
    assert min_meeting_rooms([]) == 0
