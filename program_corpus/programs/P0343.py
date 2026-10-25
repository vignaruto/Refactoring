def step_lane_platoons(lanes: list[list[tuple[float, float, bool]]], safe_gap: float) -> list[list[str]]:
    commands = []
    for lane in lanes:
        lane_cmds = ["CRUISE"]
        for idx in range(1, len(lane)):
            lead_pos, lead_v, _ = lane[idx - 1]
            fol_pos, fol_v, manual = lane[idx]
            gap = lead_pos - fol_pos
            if gap < safe_gap and fol_v > lead_v and not manual:
                lane_cmds.append("BRAKE")
            elif gap > safe_gap * 2.0 and fol_v <= lead_v and not manual:
                lane_cmds.append("ACCEL")
            else:
                lane_cmds.append("CRUISE")
        commands.append(lane_cmds)
    return commands

if __name__ == "__main__":
    cars = [(100.0, 20.0, False), (90.0, 25.0, False)]
    assert step_lane_platoons([cars], 15.0) == [["CRUISE", "BRAKE"]]
