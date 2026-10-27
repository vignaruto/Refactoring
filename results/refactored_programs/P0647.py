def estimated_wait_minutes(queue_length, agents, avg_handle_minutes, abandon_rate):
    if agents <= 0:
        return float("inf")
    expected = queue_length * (1 - abandon_rate)
    expected = expected * avg_handle_minutes / agents
    expected = expected + avg_handle_minutes / 2
    return round(expected, 1)

if __name__ == "__main__":
    assert estimated_wait_minutes(10, 2, 4, 0.1) == 20.0
    assert estimated_wait_minutes(5, 0, 4, 0.0) == float("inf")
