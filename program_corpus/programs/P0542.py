def page_rank_scores(links: dict[str, list[str]], rounds: int = 20, damping: float = 0.85) -> dict[str, float]:
    nodes = sorted(links)
    rank = {n: 1 / len(nodes) for n in nodes}
    for _ in range(rounds):
        fresh = {}
        for node in nodes:
            incoming = [src for src in nodes if node in links[src]]
            fresh[node] = (1 - damping) / len(nodes) + damping * sum(rank[s] / len(links[s]) for s in incoming)
        rank = fresh
    return {n: round(r, 3) for n, r in rank.items()}

if __name__ == "__main__":
    assert page_rank_scores({"a": ["b"], "b": ["a"]}) == {"a": 0.5, "b": 0.5}
    links = {"a": ["b", "c"], "b": ["c"], "c": ["a"]}
    scores = page_rank_scores(links)
    assert abs(sum(scores.values()) - 1.0) < 0.01
    assert scores["c"] > scores["b"]
