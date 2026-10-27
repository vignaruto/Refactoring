def find_channel_interference_pairs(towers: list[tuple[str, float, float, float, int, bool]]) -> list[tuple[str, str]]:
    conflicts = []
    for i in range(len(towers)):
        for j in range(i + 1, len(towers)):
            id_a, xa, ya, ra, ch_a, on_a = towers[i]
            id_b, xb, yb, rb, ch_b, on_b = towers[j]
            dist_sq = (xa - xb) ** 2 + (ya - yb) ** 2
            limit_sq = (ra + rb) ** 2
            condition = on_a and on_b and abs(ch_a - ch_b) <= 1
            if condition:
                condition = dist_sq < limit_sq
            if condition:
                conflicts.append((id_a, id_b))
    return conflicts

if __name__ == "__main__":
    t1 = ("T1", 0.0, 0.0, 5.0, 6, True)
    t2 = ("T2", 3.0, 4.0, 2.0, 6, True)
    assert find_channel_interference_pairs([t1, t2]) == [("T1", "T2")]
