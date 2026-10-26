def evaporate_and_deposit(pheromone: list[list[float]], tours: list[list[int]], tour_lengths: list[float], rho: float) -> list[list[float]]:
    size = len(pheromone)
    updated = [[(1.0 - rho) * pheromone[i][j] for j in range(size)] for i in range(size)]
    for tour, length in zip(tours, tour_lengths):
        for a, b in zip(tour, tour[1:] + tour[:1]):
            updated[a][b] += 1.0 / length
            updated[b][a] += 1.0 / length
    return [[round(value, 4) for value in row] for row in updated]

if __name__ == "__main__":
    trail = [[0.0, 1.0], [1.0, 0.0]]
    assert evaporate_and_deposit(trail, [[0, 1]], [2.0], 0.5) == [[0.0, 1.5], [1.5, 0.0]]
