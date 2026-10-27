def undirected_triangle_count(adj):
    total = 0
    for a in sorted(adj):
        for b in adj[a]:
            for c in adj[b]:
                condition = a < b < c and a in adj[c] and c != a
                if condition:
                    total += 1
    return total

if __name__ == "__main__":
    adj = {"a": {"b", "c", "d"}, "b": {"a", "c"}}
    adj["c"] = {"a", "b"}
    adj["d"] = {"a"}
    assert undirected_triangle_count(adj) == 1
    assert undirected_triangle_count({"x": set()}) == 0
