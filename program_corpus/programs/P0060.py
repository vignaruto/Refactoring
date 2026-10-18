from typing import Dict

def evaluate_multi_asset_portfolio_yield(equity: Dict[str, float], fixed_income: Dict[str, float], cash: Dict[str, float], base_tax: float) -> float:
    composite_return = (equity["yield"] * equity["weight"] * (1.0 - base_tax * 0.8)) + (fixed_income["yield"] * fixed_income["weight"] * (1.0 - base_tax)) + (cash["yield"] * cash["weight"] * (1.0 - base_tax * 0.5))
    return composite_return

if __name__ == "__main__":
    eq = {"yield": 0.12, "weight": 0.5}
    fi = {"yield": 0.06, "weight": 0.3}
    ca = {"yield": 0.03, "weight": 0.2}
    assert evaluate_multi_asset_portfolio_yield(eq, fi, ca, 0.15) > 0
