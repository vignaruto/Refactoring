def is_po_variance_tolerated(
    invoice_val: float, po_val: float, trusted_vendor: bool, category_critical: bool
) -> bool:
    ratio = abs(invoice_val - po_val) / max(1.0, po_val)
    cond1 = ratio <= 0.02 and trusted_vendor and invoice_val <= 50000.0
    cond2 = ratio <= 0.005 and not category_critical and invoice_val > 50000.0
    cond3 = ratio == 0.0 and not trusted_vendor
    if (cond1 or cond2 or cond3) and not (category_critical and ratio > 0.01):
        return True
    return False

if __name__ == "__main__":
    assert is_po_variance_tolerated(1010.0, 1000.0, True, False) is True
