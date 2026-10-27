import math

def proportional_fair_utilities(snr_db_grid: list[list[float]], avg_rates_mbps: list[float], bw_mhz: float) -> list[list[float]]:
    utilities = []
    for u, user_snrs in enumerate(snr_db_grid):
        row = []
        for snr_db in user_snrs:
            instantaneous_rate = bw_mhz * math.log2(1.0 + 10.0 ** (snr_db / 10.0))
            row.append(round(instantaneous_rate / max(0.1, avg_rates_mbps[u]), 4))
        utilities.append(row)
    return utilities

if __name__ == "__main__":
    grid = proportional_fair_utilities([[0.0, 10.0], [10.0, 0.0]], [1.0, 2.0], 1.0)
    assert grid[0][0] == 1.0 and grid[1][1] == 0.5
