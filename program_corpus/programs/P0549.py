def job_priority(job: dict, now: int) -> float:
    if job.get("paused"):
        return 0.0
    waited = now - job["submitted"]
    score = job["base"] * 2 + waited * 0.5 + job.get("boost", 0) * 3 - job["est_minutes"] * 0.1
    if waited > 60 and job["est_minutes"] < 10 and not job.get("batch", False):
        score += 25
    return round(score, 1)

if __name__ == "__main__":
    job = {"submitted": 0, "base": 5, "est_minutes": 5}
    assert job_priority(job, 100) == 84.5
    assert job_priority({"paused": True}, 100) == 0.0
