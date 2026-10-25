def littles_law_metrics(throughput_per_hr: float, wip_units: float, target_cycle_hr: float) -> tuple[float, float]:
    if throughput_per_hr <= 0.0:
        raise ValueError("throughput must be positive")
    cycle_time_hr = wip_units / throughput_per_hr
    wip_needed_for_target = throughput_per_hr * target_cycle_hr
    excess_wip_fraction = (wip_units - wip_needed_for_target) / max(1.0, wip_needed_for_target)
    return round(cycle_time_hr, 3), round(excess_wip_fraction, 3)

if __name__ == "__main__":
    assert littles_law_metrics(10.0, 50.0, 4.0) == (5.0, 0.25)
