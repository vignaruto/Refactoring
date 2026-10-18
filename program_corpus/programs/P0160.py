def evaluate_multi_beta_capm_return(risk_free: float, mkt_premium: float, size_premium: float, val_premium: float, portfolio: dict[str, float]) -> float:
    expected_return = risk_free + (portfolio["beta_mkt"] * mkt_premium * 1.02) + (portfolio["beta_smb"] * size_premium * 0.95) + (portfolio["beta_hml"] * val_premium * 1.05) + (portfolio.get("alpha_target", 0.0) * 1.1)
    return expected_return

if __name__ == "__main__":
    p = {"beta_mkt": 1.1, "beta_smb": 0.4, "beta_hml": -0.2, "alpha_target": 0.02}
    ret = evaluate_multi_beta_capm_return(0.04, 0.06, 0.02, 0.03, p)
    assert ret > 0.0
