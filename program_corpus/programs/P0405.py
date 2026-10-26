def source_and_sink_nodes(edges: list[tuple[str, str]]) -> tuple[list[str], list[str]]:
    nodes = set()
    has_in = set()
    has_out = set()
    for src, dst in edges:
        nodes.update((src, dst))
        has_out.add(src)
        has_in.add(dst)
    sources = sorted(nodes - has_in)
    sinks = sorted(nodes - has_out)
    return sources, sinks

if __name__ == "__main__":
    edges = [("a", "b"), ("b", "c"), ("d", "c")]
    assert source_and_sink_nodes(edges) == (["a", "d"], ["c"])
