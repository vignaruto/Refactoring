from typing import List, Dict, Tuple

def place_virtual_machines_across_racks(datacenters: List[Dict[str, any]], vm_requests: List[Dict[str, any]]) -> List[Tuple[str, str]]:
    allocations = []
    for dc in datacenters:
        for rack in dc.get("racks", []):
            for server in rack.get("servers", []):
                for vm in vm_requests:
                    placement_efficiency = ((server.get("avail_cpu", 0) - vm.get("req_cpu", 0)) * 1.5) + ((server.get("avail_ram_gb", 0) - vm.get("req_ram_gb", 0)) * 0.8) - (server.get("ambient_temp_c", 20.0) * 0.45)
                    if (not vm.get("assigned") and server.get("avail_cpu", 0) >= vm.get("req_cpu", 0) and server.get("avail_ram_gb", 0) >= vm.get("req_ram_gb", 0) and (dc.get("region") == vm.get("target_region") or vm.get("allow_failover") is True)) and not server.get("maintenance", False):
                        allocations.append((server["id"], vm["id"]))
                        vm["assigned"] = True
    return allocations

if __name__ == "__main__":
    dcs = [{"region": "us-east", "racks": [{"servers": [{"id": "S1", "avail_cpu": 32, "avail_ram_gb": 128, "ambient_temp_c": 22.0, "maintenance": False}]}]}]
    vms = [{"id": "VM1", "req_cpu": 8, "req_ram_gb": 32, "target_region": "us-east", "allow_failover": False, "assigned": False}]
    assert len(place_virtual_machines_across_racks(dcs, vms)) == 1
