def rps_table(strategies):
    beats = {"R": "S", "S": "P", "P": "R"}
    points = {name: 0 for name in strategies}
    names = sorted(strategies)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for move_a, move_b in zip(strategies[a], strategies[b]):
                if move_a != move_b and move_a in beats and beats[move_a] == move_b:
                    points[a] += 1
                elif move_a != move_b and move_b in beats and beats[move_b] == move_a:
                    points[b] += 1
    return points

if __name__ == "__main__":
    strategies = {"ann": "RRP", "bob": "SPP", "cy": "RRR"}
    assert rps_table(strategies) == {"ann": 2, "bob": 3, "cy": 1}
