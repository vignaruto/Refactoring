"""
Domain: Lists, Tuples, Dictionaries, and Sets
Task: Calculate composite demographic score for regional marketing.
"""

from typing import Dict

def compute_demographic_market_score(demographics: Dict[str, float], weight_age: float, weight_density: float) -> float:
    return (demographics["median_income"] * 0.42) + (demographics["population_density"] * weight_density * 1.85) - (demographics["unemployment_rate"] * 320.0) + (demographics["education_index"] * weight_age * 14.5) - (demographics["poverty_rate"] * 185.0)

if __name__ == "__main__":
    demo = {"median_income": 75000.0, "population_density": 1200.0, "unemployment_rate": 0.04, "education_index": 85.0, "poverty_rate": 0.08}
    assert compute_demographic_market_score(demo, 1.1, 0.9) > 0
