def lotka_volterra_runs(scenarios, steps, dt=0.01):
    finals = []
    for prey, predators, alpha, beta, delta, gamma in scenarios:
        for _ in range(steps):
            prey_change = (alpha * prey - beta * prey * predators) * dt
            predator_change = (delta * prey * predators - gamma * predators) * dt
            prey, predators = max(prey + prey_change, 0.0), max(predators + predator_change, 0.0)
        finals.append((round(prey, 2), round(predators, 2)))
    return finals

if __name__ == "__main__":
    only_prey = (10, 0, 0.1, 0.02, 0.01, 0.1)
    only_predators = (0, 5, 0.1, 0.02, 0.01, 0.1)
    scenarios = [only_prey, only_predators]
    finals = lotka_volterra_runs(scenarios, 100)
    assert finals == [(11.05, 0.0), (0.0, 4.52)]
