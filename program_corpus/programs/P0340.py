def find_zone_broker_bridges(edges: dict[str, list[str]], zones: dict[str, str], cleared: set[str]) -> list[tuple[str, str, str]]:
    bridges = []
    for src, mids in edges.items():
        for mid in mids:
            for dst in edges.get(mid, []):
                if src != dst and zones.get(src) != zones.get(dst) and mid in cleared and dst not in mids:
                    bridges.append((src, mid, dst))
    return sorted(bridges)

if __name__ == "__main__":
    g = {"n1": ["b1"], "b1": ["n2"], "n2": []}
    assert find_zone_broker_bridges(g, {"n1": "red", "b1": "dmz", "n2": "blue"}, {"b1"}) == [("n1", "b1", "n2")]
