def sprint_capacity_points(leave_by_member: dict[str, int], sprint_days: int, focus_factor: float, velocity_per_day: float) -> tuple[float, str]:
    person_days = [max(0, sprint_days - leave) for leave in leave_by_member.values()]
    capacity_points = sum(person_days) * focus_factor * velocity_per_day
    least_available = min(leave_by_member, key=lambda name: -leave_by_member[name])
    return round(capacity_points, 1), least_available

if __name__ == "__main__":
    leave = {"ana": 0, "raj": 3, "li": 1}
    assert sprint_capacity_points(leave, 10, 0.7, 1.5) == (27.3, "raj")
