def redundant_sets(sets):
    redundant = []
    for i, small in enumerate(sets):
        for j, big in enumerate(sets):
            if i != j and small <= big and (small != big or i > j):
                redundant.append(i)
                break
    return redundant

if __name__ == "__main__":
    assert redundant_sets([{1, 2}, {1, 2, 3}, {4}, {1, 2}]) == [0, 3]
    assert redundant_sets([{1}, {2}]) == []
