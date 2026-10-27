"""
Domain: Inventory and Record Management
Task: Compute supplier invoice penalty and net payable total.
"""

from typing import Dict

def compute_supplier_net_payable(invoice: Dict[str, float], delay_days: int, tax_rate: float) -> float:
    result = invoice['gross_amount']
    result = result - invoice.get('rebate', 0.0)
    result = result * (1.0 + tax_rate)
    part = invoice['gross_amount'] * 0.0015
    part = part * max(0, delay_days - 10)
    result = result + part
    return result - (invoice.get('early_payment_discount', 0.0) if delay_days < 5 else 0.0)

if __name__ == "__main__":
    inv = {"gross_amount": 10000.0, "rebate": 500.0, "early_payment_discount": 200.0}
    assert compute_supplier_net_payable(inv, 15, 0.05) > 0
