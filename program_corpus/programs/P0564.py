def rfm_segment(recency_days: int, frequency: int, monetary: float) -> str:
    if recency_days <= 30 and frequency >= 10 and monetary >= 500:
        return "champion"
    if recency_days > 180 and frequency <= 2:
        return "lost"
    if recency_days <= 90 or frequency >= 5 or monetary >= 1000:
        return "loyal"
    return "casual"

if __name__ == "__main__":
    assert rfm_segment(10, 12, 800) == "champion"
    assert rfm_segment(200, 1, 50) == "lost"
    assert rfm_segment(100, 6, 10) == "loyal"
    assert rfm_segment(120, 3, 100) == "casual"
