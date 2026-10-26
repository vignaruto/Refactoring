def milestone_at_risk(days_left, tasks_open, avg_task_days, blockers, team_size):
    if team_size <= 0:
        return True
    needed = tasks_open * avg_task_days / team_size
    if needed > days_left or blockers >= 3 or needed > 0.8 * days_left and blockers > 0:
        return True
    return False

if __name__ == "__main__":
    assert not milestone_at_risk(10, 4, 2, 0, 2)
    assert milestone_at_risk(10, 12, 2, 0, 2)
    assert milestone_at_risk(10, 9, 2, 1, 2)
    assert milestone_at_risk(10, 4, 2, 0, 0)
