def assign_harbour_tugboats(vessels: list[dict], tugs: list[dict], tide_m: float) -> dict[str, str]:
    busy = set()
    berth_plan = {}
    for vessel in sorted(vessels, key=lambda v: -v["tonnage"]):
        required_pull_t = 0.0012 * vessel["tonnage"] + 0.8 * vessel["wind_area_m2"] * (vessel["wind_kts"] / 20.0) ** 2
        for tug in tugs:
            if tug["id"] in busy:
                continue
            if tug["bollard_pull_t"] >= required_pull_t and vessel["draft_m"] <= tug["channel_depth_m"] + tide_m and (not vessel["hazmat"] or tug["firefighting"]):
                berth_plan[vessel["imo"]] = tug["id"]
                busy.add(tug["id"])
                break
    return berth_plan

if __name__ == "__main__":
    v = [{"imo": "V1", "tonnage": 30000, "wind_area_m2": 500.0, "wind_kts": 10.0, "draft_m": 11.0, "hazmat": True}]
    t = [{"id": "T1", "bollard_pull_t": 150.0, "channel_depth_m": 10.0, "firefighting": True}]
    assert assign_harbour_tugboats(v, t, 2.0) == {"V1": "T1"}
