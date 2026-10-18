from typing import Dict, List, Tuple

def audit_cluster_interlinks(cluster_a: Dict[str, any], cluster_b: Dict[str, any]) -> List[Tuple[str, str]]:
    valid_links = []
    nodes_a = cluster_a.get("nodes", [])
    nodes_b = cluster_b.get("nodes", [])
    for na in nodes_a:
        for nb in nodes_b:
            lat = na.get("latency_to_gw", 100) + nb.get("latency_to_gw", 100)
            bw = min(na.get("bandwidth", 0), nb.get("bandwidth", 0))
            link_a = lat <= 50 and bw >= 1000 and na.get("zone") == nb.get("zone")
            link_b = na.get("public_ip") is True and nb.get("vpc_peered") is True and lat <= 80
            if (link_a or link_b) and not na.get("draining", False):
                valid_links.append((na["id"], nb["id"]))
    return valid_links

if __name__ == "__main__":
    ca = {"nodes": [{"id": "A1", "latency_to_gw": 20, "bandwidth": 1500, "zone": "us-1", "draining": False}]}
    cb = {"nodes": [{"id": "B1", "latency_to_gw": 20, "bandwidth": 1500, "zone": "us-1"}]}
    assert len(audit_cluster_interlinks(ca, cb)) == 1
