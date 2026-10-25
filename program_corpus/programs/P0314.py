def kingman_wait_minutes(arrival_rate_per_hr: float, service_rate_per_hr: float, cv_arrival: float, cv_service: float) -> float:
    utilization = arrival_rate_per_hr / service_rate_per_hr
    if utilization >= 1.0 or utilization <= 0.0:
        raise ValueError("utilization must be strictly between 0 and 1")
    mean_service_min = 60.0 / service_rate_per_hr
    expected_wait_min = ((cv_arrival ** 2 + cv_service ** 2) / 2.0) * (utilization / (1.0 - utilization)) * mean_service_min
    return round(expected_wait_min, 3)

if __name__ == "__main__":
    assert kingman_wait_minutes(12.0, 15.0, 1.0, 1.0) == 16.0
