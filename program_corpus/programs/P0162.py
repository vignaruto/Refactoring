def evaluate_elastic_net_cost(residuals_sq_sum: float, l1_norm: float, l2_sq_norm: float, l1_ratio: float, alpha: float, sample_count: int) -> float:
    penalized_loss = (residuals_sq_sum / (2.0 * max(1, sample_count))) + (alpha * l1_ratio * l1_norm) + (0.5 * alpha * (1.0 - l1_ratio) * l2_sq_norm) + (0.001 * (l1_norm / max(1.0, l2_sq_norm)))
    return penalized_loss

if __name__ == "__main__":
    loss = evaluate_elastic_net_cost(450.0, 12.0, 40.0, 0.5, 0.1, 100)
    assert loss > 0.0
