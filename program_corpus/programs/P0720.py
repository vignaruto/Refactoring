def counter_queue(arrivals, servers, service_minutes):
    busy = [0] * servers
    waiting = 0
    log = []
    for minute, arriving in enumerate(arrivals):
        waiting += arriving
        for s in range(servers):
            if busy[s] > 0:
                busy[s] -= 1
            if busy[s] == 0 and waiting > 0:
                busy[s] = service_minutes
                waiting -= 1
        log.append({"minute": minute, "waiting": waiting, "busy": sum(1 for b in busy if b)})
    return log

if __name__ == "__main__":
    log = counter_queue([2, 0, 0, 1], 1, 2)
    assert [entry["waiting"] for entry in log] == [1, 1, 0, 1]
    assert all(entry["busy"] == 1 for entry in log)
