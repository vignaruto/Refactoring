def flow_shop_completion_times(processing: list[list[float]], setup: list[list[float]]) -> list[list[float]]:
    jobs, machines = len(processing), len(processing[0])
    completion = [[0.0] * machines for _ in range(jobs)]
    for i in range(jobs):
        for j in range(machines):
            previous_job_done = completion[i - 1][j] if i > 0 else 0.0
            previous_machine_done = completion[i][j - 1] if j > 0 else 0.0
            completion[i][j] = max(previous_job_done + setup[i][j], previous_machine_done) + processing[i][j]
    return completion

if __name__ == "__main__":
    assert flow_shop_completion_times([[3.0, 2.0], [1.0, 4.0]], [[0.0, 0.0], [0.0, 0.0]]) == [[3.0, 5.0], [4.0, 9.0]]
    assert flow_shop_completion_times([[3.0, 2.0], [1.0, 4.0]], [[0.0, 0.0], [1.0, 1.0]])[-1][-1] == 10.0
