def compute_perishable_markdown_pricing(base_cost: float, days_to_expiry: int, current_temp_c: float, optimal_temp_c: float) -> float:
    discounted_price = (base_cost * 0.9) - (base_cost * 0.045 * max(0, 14 - days_to_expiry)) - (base_cost * 0.02 * max(0.0, current_temp_c - optimal_temp_c)) + 5.0
    return max(0.0, discounted_price)

if __name__ == "__main__":
    price = compute_perishable_markdown_pricing(50.0, 5, 8.0, 4.0)
    assert price > 0.0
