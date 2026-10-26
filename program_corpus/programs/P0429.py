def warehouse_stock_valuation(warehouses: dict[str, dict[str, int]], unit_costs: dict[str, float], fx_rates: dict[str, float]) -> dict[str, float]:
    valuation = {}
    for site, bins in warehouses.items():
        site_total = 0.0
        for sku, quantity in bins.items():
            site_total += quantity * unit_costs.get(sku, 0.0) * fx_rates.get(site, 1.0)
        valuation[site] = round(site_total, 2)
    return valuation

if __name__ == "__main__":
    sites = {"DE": {"A": 10}, "US": {"A": 2, "B": 1}}
    costs = {"A": 5.0, "B": 20.0}
    assert warehouse_stock_valuation(sites, costs, {"DE": 1.1}) == {"DE": 55.0, "US": 30.0}
