def label_line(sku, name, qty, bin_code, width=32):
    short = name if len(name) <= 16 else name[:15] + "~"
    qty_text = str(qty).rjust(4)
    line = f"{sku:<8}{short:<16}{qty_text}"
    if bin_code:
        line = line[:width - 4] + bin_code[:4]
    return line[:width]

if __name__ == "__main__":
    label = label_line("A1", "Widget", 7, "B3")
    assert label.startswith("A1      Widget") and label.endswith("   7B3")
    assert label_line("Z9", "Extra long product name", 120, "")[8:24] == "Extra long prod~"
