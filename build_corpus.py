"""
expand_corpus_batch5.py
Automated script to generate P0201-P0250 and update program_corpus/manifest.csv
"""

import os
import ast
import csv

BASE_DIR = "program_corpus"
PROGRAMS_DIR = os.path.join(BASE_DIR, "programs")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.csv")

MODEL_ID = "gemini-2.5-pro"
PROMPT_VER = "v5.0-expansion"
BATCH_ID = "Batch 5"

PROGRAMS_DATA = {
    # 1. NONE (8 programs: P0201 - P0208)
    "P0201": {
        "domain": "Numerical Computation",
        "task": "Simpson 1/3 numerical integration of polynomial functions",
        "category": "None",
        "code": '''def simpsons_one_third_rule(
    coeffs: list[float], a: float, b: float, n_intervals: int
) -> float:
    if n_intervals % 2 != 0:
        raise ValueError("Number of intervals must be even")
    h = (b - a) / float(n_intervals)
    def poly(x: float) -> float:
        val = 0.0
        for p, c in enumerate(coeffs):
            val += c * (x ** p)
        return val
    total = poly(a) + poly(b)
    for i in range(1, n_intervals):
        xi = a + i * h
        if i % 2 == 1:
            total += 4.0 * poly(xi)
        else:
            total += 2.0 * poly(xi)
    return total * (h / 3.0)

if __name__ == "__main__":
    area = simpsons_one_third_rule([0.0, 0.0, 1.0], 0.0, 3.0, 6)
    assert round(area, 2) == 9.0
'''
    },
    "P0202": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Min-max normalization of numeric feature vector",
        "category": "None",
        "code": '''def min_max_normalize_vector(
    values: list[float]
) -> list[float]:
    if not values:
        return []
    min_val = min(values)
    max_val = max(values)
    spread = max_val - min_val
    if spread == 0.0:
        return [0.0] * len(values)
    normalized = []
    for x in values:
        norm = (x - min_val) / spread
        normalized.append(round(norm, 4))
    return normalized

if __name__ == "__main__":
    nums = [10.0, 20.0, 30.0, 40.0, 50.0]
    res = min_max_normalize_vector(nums)
    assert res[0] == 0.0 and res[-1] == 1.0
'''
    },
    "P0203": {
        "domain": "String Processing & Text Analysis",
        "task": "Calculate normalized Levenshtein token similarity ratio",
        "category": "None",
        "code": '''def compute_token_overlap_ratio(text_a: str, text_b: str) -> float:
    tokens_a = set(text_a.lower().split())
    tokens_b = set(text_b.lower().split())
    if not tokens_a and not tokens_b:
        return 1.0
    if not tokens_a or not tokens_b:
        return 0.0
    common = tokens_a.intersection(tokens_b)
    union = tokens_a.union(tokens_b)
    return len(common) / float(len(union))

if __name__ == "__main__":
    score = compute_token_overlap_ratio("quick brown fox", "brown fox dog")
    assert round(score, 2) == 0.50
'''
    },
    "P0204": {
        "domain": "Searching and Sorting",
        "task": "Ternary search for finding peak in strictly unimodal array",
        "category": "None",
        "code": '''def ternary_search_unimodal(arr: list[float]) -> int:
    left = 0
    right = len(arr) - 1
    while right - left > 2:
        m1 = left + (right - left) // 3
        m2 = right - (right - left) // 3
        if arr[m1] < arr[m2]:
            left = m1
        else:
            right = m2
    peak_idx = left
    for idx in range(left + 1, right + 1):
        if arr[idx] > arr[peak_idx]:
            peak_idx = idx
    return peak_idx

if __name__ == "__main__":
    assert ternary_search_unimodal([1.0, 3.0, 7.0, 12.0, 9.0, 4.0, 2.0]) == 3
'''
    },
    "P0205": {
        "domain": "Matrix & Grid Operations",
        "task": "Check if a 2D integer matrix is a valid Toeplitz matrix",
        "category": "None",
        "code": '''def is_toeplitz_matrix(matrix: list[list[int]]) -> bool:
    rows = len(matrix)
    cols = len(matrix[0])
    flat_len = (rows - 1) * (cols - 1)
    for k in range(flat_len):
        r = k // (cols - 1)
        c = k % (cols - 1)
        if matrix[r][c] != matrix[r + 1][c + 1]:
            return False
    return True

if __name__ == "__main__":
    m = [[1, 2, 3, 4], [5, 1, 2, 3], [9, 5, 1, 2]]
    assert is_toeplitz_matrix(m) is True
'''
    },
    "P0206": {
        "domain": "Data Aggregation and Statistics",
        "task": "Compute interquartile range (IQR) and outlier fences",
        "category": "None",
        "code": '''def compute_iqr_fences(data: list[float]) -> dict[str, float]:
    if len(data) < 4:
        raise ValueError("At least 4 observations required")
    sorted_d = sorted(data)
    n = len(sorted_d)
    q1 = sorted_d[n // 4]
    q3 = sorted_d[(3 * n) // 4]
    iqr = q3 - q1
    return {
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "lower_fence": q1 - 1.5 * iqr,
        "upper_fence": q3 + 1.5 * iqr
    }

if __name__ == "__main__":
    res = compute_iqr_fences([10.0, 12.0, 14.0, 15.0, 18.0, 20.0, 22.0, 50.0])
    assert res["iqr"] == 8.0
'''
    },
    "P0207": {
        "domain": "Inventory and Record Management",
        "task": "Calculate inventory turnover ratio and average days sales",
        "category": "None",
        "code": '''def compute_inventory_turnover_days(
    cost_of_goods_sold: float, beg_inventory: float, end_inventory: float
) -> dict[str, float]:
    avg_inventory = (beg_inventory + end_inventory) / 2.0
    if avg_inventory <= 0.0:
        raise ValueError("Average inventory must be positive")
    turns = cost_of_goods_sold / avg_inventory
    days = 365.0 / turns if turns > 0.0 else 0.0
    return {
        "turnover_ratio": round(turns, 2),
        "days_in_inventory": round(days, 1)
    }

if __name__ == "__main__":
    res = compute_inventory_turnover_days(400000.0, 80000.0, 120000.0)
    assert res["turnover_ratio"] == 4.0
'''
    },
    "P0208": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Earliest deadline first single processor task schedule simulation",
        "category": "None",
        "code": '''def simulate_edf_scheduling(
    tasks: list[dict[str, int]]
) -> list[str]:
    sorted_tasks = sorted(tasks, key=lambda t: t.get("deadline", 0))
    schedule_order = []
    clock = 0
    for task in sorted_tasks:
        clock += task.get("execution_time", 1)
        schedule_order.append(task.get("name", "anon"))
    return schedule_order

if __name__ == "__main__":
    t_list = [{"name": "T1", "deadline": 10}, {"name": "T2", "deadline": 5}]
    order = simulate_edf_scheduling(t_list)
    assert order == ["T2", "T1"]
'''
    },

    # 2. LONG STATEMENT ONLY (6 programs: P0209 - P0214)
    "P0209": {
        "domain": "Numerical Computation",
        "task": "Evaluate atmospheric refractive bending and optical path dispersion",
        "category": "Long statement only",
        "code": '''import math

def calculate_atmospheric_optical_refraction(zenith_angle_deg: float, temp_kelvin: float, pressure_hpa: float, humidity_pct: float) -> float:
    refraction_arcsec = (pressure_hpa / 1013.25) * (288.15 / temp_kelvin) * ((57.83 * math.tan(math.radians(zenith_angle_deg))) - (0.067 * (math.tan(math.radians(zenith_angle_deg)) ** 3))) * (1.0 - 0.00015 * humidity_pct)
    return refraction_arcsec

if __name__ == "__main__":
    assert calculate_atmospheric_optical_refraction(45.0, 290.0, 1010.0, 50.0) > 0.0
'''
    },
    "P0210": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Calculate multi-currency foreign exchange synthetic cross-arbitrage spread",
        "category": "Long statement only",
        "code": '''def evaluate_fx_triangular_spread(rates: dict[str, float], fee_rate: float, volume_usd: float) -> float:
    synthetic_yield = (((volume_usd * rates["eur_usd"] * (1.0 - fee_rate)) * rates["gbp_eur"] * (1.0 - fee_rate)) * rates["usd_gbp"] * (1.0 - fee_rate)) - volume_usd - (fee_rate * volume_usd * 0.5)
    return synthetic_yield

if __name__ == "__main__":
    r = {"eur_usd": 1.08, "gbp_eur": 1.16, "usd_gbp": 0.80}
    assert evaluate_fx_triangular_spread(r, 0.001, 100000.0) != 0.0
'''
    },
    "P0211": {
        "domain": "String Processing & Text Analysis",
        "task": "Compute Coleman-Liau linguistic readability index from character histograms",
        "category": "Long statement only",
        "code": '''def compute_coleman_liau_readability(letters_count: int, words_count: int, sentences_count: int) -> float:
    coleman_score = (0.0588 * (float(letters_count) / float(max(1, words_count)) * 100.0)) - (0.296 * (float(sentences_count) / float(max(1, words_count)) * 100.0)) - 15.8 + 0.05
    return coleman_score

if __name__ == "__main__":
    score = compute_coleman_liau_readability(1500, 300, 15)
    assert score > 0.0
'''
    },
    "P0212": {
        "domain": "Data Aggregation and Statistics",
        "task": "Compute exponential smoothing Holt-Winters trend and seasonal damping",
        "category": "Long statement only",
        "code": '''def evaluate_holt_winters_forecast(base_level: float, trend_slope: float, phi_damping: float, horizon_steps: int, seasonal_factor: float) -> float:
    forecast_value = (base_level + (sum(phi_damping ** i for i in range(1, horizon_steps + 1)) * trend_slope)) * (1.0 + seasonal_factor * 0.1) + 2.5
    return forecast_value

if __name__ == "__main__":
    res = evaluate_holt_winters_forecast(100.0, 2.5, 0.95, 4, 0.1)
    assert res > 0.0
'''
    },
    "P0213": {
        "domain": "Inventory and Record Management",
        "task": "Compute automated cold-storage perishable markdown depreciation",
        "category": "Long statement only",
        "code": '''def compute_perishable_markdown_pricing(base_cost: float, days_to_expiry: int, current_temp_c: float, optimal_temp_c: float) -> float:
    discounted_price = (base_cost * 0.9) - (base_cost * 0.045 * max(0, 14 - days_to_expiry)) - (base_cost * 0.02 * max(0.0, current_temp_c - optimal_temp_c)) + 5.0
    return max(0.0, discounted_price)

if __name__ == "__main__":
    price = compute_perishable_markdown_pricing(50.0, 5, 8.0, 4.0)
    assert price > 0.0
'''
    },
    "P0214": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Simulate electromagnetic induction Lorentz drag in eddy-current braking",
        "category": "Long statement only",
        "code": '''def calculate_eddy_current_braking_force(conductivity: float, thickness_m: float, disk_radius_m: float, b_field_tesla: float, rpm: float) -> float:
    retarding_torque = (0.25 * conductivity * thickness_m * (disk_radius_m ** 4) * (b_field_tesla ** 2) * (rpm * 0.10472)) * (1.0 - (0.015 * (rpm * 0.10472 * 0.05))) + 1.2
    return retarding_torque

if __name__ == "__main__":
    t = calculate_eddy_current_braking_force(3.5e7, 0.01, 0.2, 1.2, 1200.0)
    assert t > 0.0
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0215 - P0220)
    "P0215": {
        "domain": "Numerical Computation",
        "task": "Compute matrix LU decomposition with Doolittle's algorithm",
        "category": "Nested loop only",
        "code": '''def lu_decomposition_doolittle(
    matrix: list[list[float]]
) -> tuple[list[list[float]], list[list[float]]]:
    n = len(matrix)
    lower = [[0.0] * n for _ in range(n)]
    upper = [[0.0] * n for _ in range(n)]
    for i in range(n):
        lower[i][i] = 1.0
        for k in range(i, n):
            sum_u = 0.0
            for j in range(i):
                sum_u += lower[i][j] * upper[j][k]
            upper[i][k] = matrix[i][k] - sum_u
        for k in range(i + 1, n):
            sum_l = 0.0
            for j in range(i):
                sum_l += lower[k][j] * upper[j][i]
            lower[k][i] = (matrix[k][i] - sum_l) / upper[i][i]
    return lower, upper

if __name__ == "__main__":
    m = [[2.0, -1.0], [-4.0, 6.0]]
    l, u = lu_decomposition_doolittle(m)
    assert l[1][0] == -2.0
'''
    },
    "P0216": {
        "domain": "Searching and Sorting",
        "task": "Pancake sorting algorithm for integers using prefix flips",
        "category": "Nested loop only",
        "code": '''def pancake_sort(items: list[int]) -> list[int]:
    arr = list(items)
    curr_size = len(arr)
    while curr_size > 1:
        max_idx = 0
        for i in range(1, curr_size):
            if arr[i] > arr[max_idx]:
                max_idx = i
        if max_idx != curr_size - 1:
            arr[:max_idx + 1] = reversed(arr[:max_idx + 1])
            arr[:curr_size] = reversed(arr[:curr_size])
        curr_size -= 1
    return arr

if __name__ == "__main__":
    assert pancake_sort([3, 2, 4, 1]) == [1, 2, 3, 4]
'''
    },
    "P0217": {
        "domain": "Matrix & Grid Operations",
        "task": "Compute cumulative integral image (summed-area table) for 2D matrix",
        "category": "Nested loop only",
        "code": '''def compute_integral_image(grid: list[list[int]]) -> list[list[int]]:
    h = len(grid)
    w = len(grid[0])
    integral = [[0] * w for _ in range(h)]
    for r in range(h):
        for c in range(w):
            val = grid[r][c]
            top = integral[r - 1][c] if r > 0 else 0
            left = integral[r][c - 1] if c > 0 else 0
            diag = integral[r - 1][c - 1] if r > 0 and c > 0 else 0
            integral[r][c] = val + top + left - diag
    return integral

if __name__ == "__main__":
    g = [[1, 2], [3, 4]]
    res = compute_integral_image(g)
    assert res[1][1] == 10
'''
    },
    "P0218": {
        "domain": "String Processing & Text Analysis",
        "task": "Compute shortest common supersequence length using dynamic programming",
        "category": "Nested loop only",
        "code": '''def scs_length(str1: str, str2: str) -> int:
    m = len(str1)
    n = len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        for j in range(n + 1):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i
            elif str1[i - 1] == str2[j - 1]:
                dp[i][j] = 1 + dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

if __name__ == "__main__":
    assert scs_length("geek", "eke") == 5
'''
    },
    "P0219": {
        "domain": "Graph or Tree Traversal",
        "task": "Tarjan-inspired strongly connected components graph vertex reachability",
        "category": "Nested loop only",
        "code": '''def compute_pair_reachability_matrix(adj: list[list[int]]) -> list[list[int]]:
    n = len(adj)
    reach = [row[:] for row in adj]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if reach[i][j] == 0:
                    if reach[i][k] == 1 and reach[k][j] == 1:
                        reach[i][j] = 1
    return reach

if __name__ == "__main__":
    g = [[1, 1, 0], [0, 1, 1], [0, 0, 1]]
    res = compute_pair_reachability_matrix(g)
    assert res[0][2] == 1
'''
    },
    "P0220": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Simulate particle diffusion across porous membrane lattice barrier",
        "category": "Nested loop only",
        "code": '''def step_porous_diffusion(grid: list[list[float]], coeff: float) -> list[list[float]]:
    h = len(grid)
    w = len(grid[0])
    nxt = [row[:] for row in grid]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            flow = 0.0
            for dr in (-1, 1):
                flow += grid[r + dr][c] - grid[r][c]
            for dc in (-1, 1):
                flow += grid[r][c + dc] - grid[r][c]
            nxt[r][c] += flow * coeff
    return nxt

if __name__ == "__main__":
    m = [[0.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 0.0]]
    res = step_porous_diffusion(m, 0.1)
    assert res[1][1] < 10.0
'''
    },

    # 4. COMPLEX CONDITIONAL ONLY (6 programs: P0221 - P0226)
    "P0221": {
        "domain": "Numerical Computation",
        "task": "Verify non-linear optimization convergence with Wolfe conditions",
        "category": "Complex conditional only",
        "code": '''def is_wolfe_step_satisfied(
    f_curr: float, f_prev: float, grad_curr: float, grad_prev: float, alpha: float
) -> bool:
    armijo = f_curr <= f_prev + 1e-4 * alpha * grad_prev
    curvature = grad_curr >= 0.9 * grad_prev
    strong_curv = abs(grad_curr) <= 0.9 * abs(grad_prev)
    if (armijo and curvature) or (strong_curv and f_curr < f_prev and alpha > 1e-3):
        return True
    return False

if __name__ == "__main__":
    assert is_wolfe_step_satisfied(-1.0, 0.0, 0.5, 1.0, 0.1) is True
'''
    },
    "P0222": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Validate microservice REST payload schema and access permissions",
        "category": "Complex conditional only",
        "code": '''def is_rest_request_authorized(
    token: dict[str, any], payload: dict[str, any], bypass_internal: bool
) -> bool:
    is_admin = token.get("role") == "admin"
    valid_sig = token.get("signature_verified") is True
    size_ok = payload.get("bytes_len", 0) <= 1048576
    rate_ok = not token.get("throttled", False)
    rule_admin = is_admin and valid_sig and size_ok
    rule_internal = bypass_internal and valid_sig and not token.get("revoked", False)
    if (rule_admin or rule_internal) and rate_ok:
        return True
    return False

if __name__ == "__main__":
    t = {"role": "admin", "signature_verified": True, "throttled": False}
    p = {"bytes_len": 5000}
    assert is_rest_request_authorized(t, p, False) is True
'''
    },
    "P0223": {
        "domain": "String Processing & Text Analysis",
        "task": "Classify URI scheme safety against SSRF attack heuristics",
        "category": "Complex conditional only",
        "code": '''def is_safe_external_uri(
    uri: str, allow_custom_ports: bool, allow_https_only: bool
) -> bool:
    lower_uri = uri.lower()
    is_http = lower_uri.startswith("http://")
    is_https = lower_uri.startswith("https://")
    is_loopback = "localhost" in lower_uri or "127.0.0.1" in lower_uri
    is_internal = "192.168." in lower_uri or "10." in lower_uri
    if ((is_https or (is_http and not allow_https_only)) and not is_loopback) and not is_internal:
        return True
    return False

if __name__ == "__main__":
    assert is_safe_external_uri("https://api.external-service.org/v1", False, True) is True
'''
    },
    "P0224": {
        "domain": "Data Aggregation and Statistics",
        "task": "Authorize high-value securities margin trading order",
        "category": "Complex conditional only",
        "code": '''def is_margin_trade_approved(
    account: dict[str, float], order: dict[str, any], regulator_halt: bool
) -> bool:
    equity = account.get("equity", 0.0)
    debt = account.get("margin_debt", 0.0)
    maintenance_ratio = equity / max(1.0, debt + order.get("amount", 0.0))
    tier_ok = account.get("kyc_tier", 1) >= 2
    rule_std = maintenance_ratio >= 0.30 and equity >= 25000.0 and tier_ok
    rule_sub = equity >= 100000.0 and tier_ok and not order.get("is_penny_stock", False)
    if (rule_std or rule_sub) and not regulator_halt:
        return True
    return False

if __name__ == "__main__":
    acc = {"equity": 50000.0, "margin_debt": 10000.0, "kyc_tier": 2}
    ord_info = {"amount": 5000.0, "is_penny_stock": False}
    assert is_margin_trade_approved(acc, ord_info, False) is True
'''
    },
    "P0225": {
        "domain": "Inventory and Record Management",
        "task": "Validate bonded warehouse duty drawback reimbursement claim",
        "category": "Complex conditional only",
        "code": '''def is_duty_drawback_eligible(
    claim: dict[str, any], days_since_export: int, customs_verified: bool
) -> bool:
    val = claim.get("claimed_refund_usd", 0.0)
    re_export = claim.get("re_exported_unchanged") is True
    has_cert = claim.get("certificate_of_origin") is True
    valid_window = days_since_export <= 1095 and val <= 250000.0
    if ((re_export and has_cert and valid_window) or (customs_verified and valid_window)) and val > 0.0:
        return True
    return False

if __name__ == "__main__":
    cl = {"claimed_refund_usd": 15000.0, "re_exported_unchanged": True, "certificate_of_origin": True}
    assert is_duty_drawback_eligible(cl, 180, True) is True
'''
    },
    "P0226": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Authorize railway signaling priority train interlocking passage",
        "category": "Complex conditional only",
        "code": '''def is_interlocking_passage_granted(
    train: dict[str, any], block: dict[str, any], emergency_stop_active: bool
) -> bool:
    speed_ok = train.get("current_speed_kph", 0) <= block.get("speed_limit_kph", 120)
    clear = block.get("occupancy_status") == "CLEAR"
    switch_locked = block.get("switch_points_locked") is True
    prio_express = train.get("service_type") == "EXPRESS" and clear
    if (clear and switch_locked and speed_ok) or (prio_express and not emergency_stop_active):
        return True
    return False

if __name__ == "__main__":
    t = {"current_speed_kph": 90, "service_type": "EXPRESS"}
    b = {"speed_limit_kph": 120, "occupancy_status": "CLEAR", "switch_points_locked": True}
    assert is_interlocking_passage_granted(t, b, False) is True
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (6 programs: P0227 - P0232)
    "P0227": {
        "domain": "Numerical Computation",
        "task": "Multi-dimensional radial basis function surface approximation",
        "category": "Long statement and nested loop",
        "code": '''import math

def rbf_surface_interpolation(grid_x: list[float], grid_y: list[float], centers: list[tuple[float, float, float]], epsilon: float) -> list[list[float]]:
    surface = []
    for x in grid_x:
        row = []
        for y in grid_y:
            height = sum(w * math.sqrt(1.0 + (epsilon**2) * ((x - cx)**2 + (y - cy)**2)) for cx, cy, w in centers) + (0.01 * (x**2 + y**2))
            row.append(height)
        surface.append(row)
    return surface

if __name__ == "__main__":
    c = [(0.0, 0.0, 1.0), (1.0, 1.0, 2.0)]
    res = rbf_surface_interpolation([0.5], [0.5], c, 0.5)
    assert len(res) == 1
'''
    },
    "P0228": {
        "domain": "Searching and Sorting",
        "task": "Compute pairwise angular cosine similarity across high-dimensional embeddings",
        "category": "Long statement and nested loop",
        "code": '''def compute_pairwise_embedding_similarity(embeddings: list[list[float]]) -> list[list[float]]:
    n = len(embeddings)
    sim_matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            sim_matrix[i][j] = sum(embeddings[i][k] * embeddings[j][k] for k in range(len(embeddings[i]))) / (((sum(x**2 for x in embeddings[i])**0.5) * (sum(y**2 for y in embeddings[j])**0.5)) + 1e-9)
    return sim_matrix

if __name__ == "__main__":
    vecs = [[1.0, 0.0], [0.0, 1.0]]
    res = compute_pairwise_embedding_similarity(vecs)
    assert res[0][0] > 0.99
'''
    },
    "P0229": {
        "domain": "Matrix & Grid Operations",
        "task": "Apply Laplacian edge detector convolution kernel on grayscale image raster",
        "category": "Long statement and nested loop",
        "code": '''def apply_laplacian_edge_filter(raster: list[list[float]], scale_gain: float) -> list[list[float]]:
    h = len(raster)
    w = len(raster[0])
    edges = [[0.0] * w for _ in range(h)]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            edges[r][c] = ((raster[r-1][c] + raster[r+1][c] + raster[r][c-1] + raster[r][c+1] - 4.0 * raster[r][c]) * scale_gain) + (0.5 * (raster[r-1][c-1] + raster[r+1][c+1] - 2.0 * raster[r][c]))
    return edges

if __name__ == "__main__":
    m = [[1.0]*3 for _ in range(3)]
    res = apply_laplacian_edge_filter(m, 1.0)
    assert res[1][1] == 0.0
'''
    },
    "P0230": {
        "domain": "Data Aggregation and Statistics",
        "task": "Compute double-rolling covariance across multi-variate financial time series",
        "category": "Long statement and nested loop",
        "code": '''def evaluate_cross_asset_rolling_cov(series_a: list[list[float]], series_b: list[list[float]]) -> list[list[float]]:
    m = len(series_a)
    n = len(series_b)
    table = [[0.0] * n for _ in range(m)]
    for i in range(m):
        for j in range(n):
            table[i][j] = sum((series_a[i][t] - (sum(series_a[i]) / len(series_a[i]))) * (series_b[j][t] - (sum(series_b[j]) / len(series_b[j]))) for t in range(len(series_a[i]))) / float(max(1, len(series_a[i]) - 1))
    return table

if __name__ == "__main__":
    a = [[1.0, 2.0, 3.0]]
    b = [[2.0, 4.0, 6.0]]
    res = evaluate_cross_asset_rolling_cov(a, b)
    assert len(res) == 1
'''
    },
    "P0231": {
        "domain": "Inventory and Record Management",
        "task": "Calculate multi-echelon supply hub replenishment costs",
        "category": "Long statement and nested loop",
        "code": '''def calculate_echelon_freight_network(depots: list[dict[str, float]], retailers: list[dict[str, float]]) -> list[list[float]]:
    matrix = []
    for d in depots:
        row = []
        for r in retailers:
            tariff = (d["base_tariff"] * 1.08) + (((d["coord_x"] - r["coord_x"])**2 + (d["coord_y"] - r["coord_y"])**2)**0.5 * d["ton_mile_cost"] * (1.0 + r.get("fuel_index", 0.15))) + (r["pallet_count"] * 18.5)
            row.append(tariff)
        matrix.append(row)
    return matrix

if __name__ == "__main__":
    dp = [{"base_tariff": 100.0, "coord_x": 0.0, "coord_y": 0.0, "ton_mile_cost": 0.5}]
    rt = [{"coord_x": 30.0, "coord_y": 40.0, "pallet_count": 5.0}]
    assert len(calculate_echelon_freight_network(dp, rt)) == 1
'''
    },
    "P0232": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Simulate electrostatic point dipole potential grid interaction",
        "category": "Long statement and nested loop",
        "code": '''def compute_dipole_potential_mesh(dipoles: list[dict[str, float]], grid_coords: list[tuple[float, float]]) -> list[float]:
    potentials = []
    for gx, gy in grid_coords:
        acc = 0.0
        for dip in dipoles:
            rx = gx - dip["x"]
            ry = gy - dip["y"]
            acc += (8.98755e9 * ((dip["moment_x"] * rx + dip["moment_y"] * ry) / ((rx**2 + ry**2 + 0.01)**1.5))) * (1.0 - 0.002 * (rx**2 + ry**2)**0.5)
        potentials.append(acc)
    return potentials

if __name__ == "__main__":
    d = [{"x": 0.0, "y": 0.0, "moment_x": 1.0, "moment_y": 0.0}]
    pts = [(1.0, 1.0)]
    res = compute_dipole_potential_mesh(d, pts)
    assert len(res) == 1
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0233 - P0238)
    "P0233": {
        "domain": "Numerical Computation",
        "task": "Evaluate atmospheric acoustic Doppler shift with temperature and wind layers",
        "category": "Long statement and complex conditional",
        "code": '''import math

def calculate_doppler_acoustic_frequency(source_freq: float, temp_c: float, wind_ms: float, observer_vel: float, source_vel: float) -> float:
    shifted_frequency = source_freq * ((331.3 * math.sqrt(1.0 + temp_c / 273.15) + wind_ms - observer_vel) / (331.3 * math.sqrt(1.0 + temp_c / 273.15) + wind_ms - source_vel)) * (1.0 - 0.0015 * abs(wind_ms))
    valid_speeds = abs(source_vel) < 300.0 and abs(observer_vel) < 300.0
    valid_temp = temp_c >= -50.0 and temp_c <= 60.0
    if ((valid_speeds and valid_temp and source_freq > 20.0) or (abs(wind_ms) < 5.0 and valid_temp)) and not source_freq > 20000.0:
        return shifted_frequency
    return 0.0

if __name__ == "__main__":
    f = calculate_doppler_acoustic_frequency(1000.0, 20.0, 5.0, 0.0, 25.0)
    assert f > 1000.0
'''
    },
    "P0234": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Compute high-net-worth wealth management portfolio rebalancing fee",
        "category": "Long statement and complex conditional",
        "code": '''def evaluate_portfolio_rebalance_fee(client: dict[str, float], assets: dict[str, float]) -> float:
    total_fee = (assets["aum_usd"] * 0.0075 * (1.0 - client.get("loyalty_discount", 0.05))) + (client.get("trades_count", 1) * 12.5) + (assets.get("illiquid_private_equity", 0.0) * 0.002) - 150.0
    is_platinum = client.get("tier") == 3.0 and assets.get("aum_usd", 0.0) >= 5000000.0
    is_gold = client.get("tier") == 2.0 and assets.get("aum_usd", 0.0) >= 1000000.0
    if ((is_platinum and not client.get("has_dispute", False)) or (is_gold and client.get("tenure_years", 0) >= 5)) and not client.get("frozen", False):
        return max(0.0, total_fee * 0.85)
    return max(0.0, total_fee)

if __name__ == "__main__":
    cl = {"tier": 3.0, "has_dispute": False, "frozen": False}
    ass = {"aum_usd": 6000000.0, "trades_count": 10}
    assert evaluate_portfolio_rebalance_fee(cl, ass) > 0.0
'''
    },
    "P0235": {
        "domain": "String Processing & Text Analysis",
        "task": "Classify TLS certificate common name format and cryptographic entropy",
        "category": "Long statement and complex conditional",
        "code": '''def score_ssl_certificate_validity(cert: dict[str, any], domain_fqdn: str) -> float:
    sec_score = (int(cert.get("key_bits", 2048)) / 64.0) + (len(domain_fqdn) * 0.4) + (sum(c.isupper() for c in cert.get("issuer", "")) * 1.5) - (cert.get("revocation_checks_failed", 0) * 25.0) + 20.0
    san_match = domain_fqdn in cert.get("san_list", [])
    valid_dates = cert.get("days_remaining", 0) >= 14 and cert.get("days_remaining", 0) <= 398
    trusted_ca = cert.get("ca_verified") is True
    if ((san_match and valid_dates and trusted_ca) or (cert.get("is_wildcard") is True and valid_dates)) and not cert.get("revoked", False):
        return sec_score
    return 0.0

if __name__ == "__main__":
    c = {"key_bits": 4096, "san_list": ["example.org"], "days_remaining": 120, "ca_verified": True, "revoked": False}
    assert score_ssl_certificate_validity(c, "example.org") > 0.0
'''
    },
    "P0236": {
        "domain": "Data Aggregation and Statistics",
        "task": "Compute solar photovoltaic park daily revenue with feed-in curtailment",
        "category": "Long statement and complex conditional",
        "code": '''def calculate_photovoltaic_revenue(plant: dict[str, float], grid_status: dict[str, any]) -> float:
    generation_revenue = (plant["irradiance_wm2"] * plant["collector_area_sqm"] * 0.185 * (1.0 - 0.004 * max(0.0, plant["cell_temp_c"] - 25.0)) * 0.001) * plant["tariff_usd_kwh"] * 8.0
    irr_ok = plant.get("irradiance_wm2", 0.0) >= 150.0 and plant.get("irradiance_wm2", 0.0) <= 1200.0
    temp_safe = plant.get("cell_temp_c", 25.0) <= 75.0
    if ((irr_ok and temp_safe and not grid_status.get("grid_overfrequency_trip", False)) or (plant.get("has_battery_storage") is True and irr_ok)) and not plant.get("inverter_fault", False):
        return generation_revenue
    return 0.0

if __name__ == "__main__":
    p = {"irradiance_wm2": 850.0, "collector_area_sqm": 5000.0, "cell_temp_c": 45.0, "tariff_usd_kwh": 0.08}
    g = {"grid_overfrequency_trip": False}
    assert calculate_photovoltaic_revenue(p, g) > 0.0
'''
    },
    "P0237": {
        "domain": "Inventory and Record Management",
        "task": "Calculate pharmaceutical clinical drug inventory reserve under FDA compliance",
        "category": "Long statement and complex conditional",
        "code": '''def evaluate_clinical_drug_reserve(trial: dict[str, float], compliance: dict[str, any]) -> float:
    reserve_capital = (trial["active_participants"] * trial["doses_per_month"] * trial["unit_synthesis_cost"] * 1.25) + (trial.get("cold_chain_monitoring_usd", 2500.0)) - (trial.get("sponsor_rebate", 5000.0)) + 10000.0
    phase_ok = compliance.get("phase") in ("Phase2", "Phase3")
    audited = compliance.get("gcp_certified") is True
    no_violations = compliance.get("form_483_issued") is not True
    if ((phase_ok and audited and no_violations) or (compliance.get("fast_track_granted") is True and audited)) and trial.get("active_participants", 0) > 10:
        return reserve_capital
    return 0.0

if __name__ == "__main__":
    tr = {"active_participants": 100.0, "doses_per_month": 4.0, "unit_synthesis_cost": 50.0}
    comp = {"phase": "Phase3", "gcp_certified": True, "form_483_issued": False}
    assert evaluate_clinical_drug_reserve(tr, comp) > 0.0
'''
    },
    "P0238": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Simulate commercial gas turbine combustor flameout detection and reignition",
        "category": "Long statement and complex conditional",
        "code": '''def check_turbine_combustor_flameout(combustor: dict[str, float], controller: dict[str, any]) -> float:
    flame_stability_margin = ((combustor["burner_temp_c"] - 800.0) * 0.45) + (combustor["inlet_pressure_bar"] * 8.2) - (combustor["airflow_kg_s"] * 2.1) + (combustor.get("methane_fuel_ratio", 0.05) * 450.0)
    temp_low = combustor.get("burner_temp_c", 1000.0) < 850.0
    pressure_drop = combustor.get("delta_p_bar", 0.0) > 2.5
    if ((temp_low and pressure_drop and not controller.get("reignition_active", False)) or (combustor.get("optical_flame_lost") is True and temp_low)) and not controller.get("emergency_scram", False):
        return flame_stability_margin
    return 0.0

if __name__ == "__main__":
    c = {"burner_temp_c": 820.0, "inlet_pressure_bar": 15.0, "airflow_kg_s": 25.0, "delta_p_bar": 3.0, "optical_flame_lost": True}
    ctrl = {"reignition_active": False, "emergency_scram": False}
    assert check_turbine_combustor_flameout(c, ctrl) != 0.0
'''
    },

    # 7. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0239 - P0244)
    "P0239": {
        "domain": "Numerical Computation",
        "task": "Search 2D autonomous dynamical phase portrait for limit cycle attractors",
        "category": "Nested loop and complex conditional",
        "code": '''def locate_phase_portrait_attractors(
    mesh_u: list[float], mesh_v: list[float], friction: float
) -> list[tuple[float, float]]:
    attractors = []
    for u in mesh_u:
        for v in mesh_v:
            divergence = -friction + 3.0 * (u**2)
            jacobian_det = u * v - friction**2
            c1 = divergence < 0.0 and jacobian_det > 0.0 and friction > 0.05
            c2 = abs(divergence) < 0.01 and jacobian_det > 1.0
            c3 = not (u == 0.0 and v == 0.0)
            if (c1 or c2) and c3 and (u > -2.0 or friction < 0.5):
                attractors.append((u, v))
    return attractors

if __name__ == "__main__":
    assert len(locate_phase_portrait_attractors([0.2], [1.5], 0.1)) == 1
'''
    },
    "P0240": {
        "domain": "Searching and Sorting",
        "task": "Filter logistics shipping container load compatibilities across weight tiers",
        "category": "Nested loop and complex conditional",
        "code": '''def match_compatible_container_pairs(
    group_a: list[dict[str, any]], group_b: list[dict[str, any]]
) -> list[tuple[str, str]]:
    valid_pairs = []
    for c1 in group_a:
        for c2 in group_b:
            weight_sum = c1.get("weight_tons", 0) + c2.get("weight_tons", 0)
            same_dest = c1.get("port") == c2.get("port")
            haz_conflict = c1.get("is_hazardous") is True and c2.get("is_hazardous") is True
            rule_std = weight_sum <= 45 and same_dest and not haz_conflict
            rule_reefer = c1.get("reefer") is True and c2.get("reefer") is True and same_dest
            if (rule_std or rule_reefer) and not c1.get("hold_flag", False):
                valid_pairs.append((c1["id"], c2["id"]))
    return valid_pairs

if __name__ == "__main__":
    g1 = [{"id": "C1", "weight_tons": 20, "port": "ROT", "is_hazardous": False}]
    g2 = [{"id": "C2", "weight_tons": 22, "port": "ROT", "is_hazardous": False}]
    assert len(match_compatible_container_pairs(g1, g2)) == 1
'''
    },
    "P0241": {
        "domain": "Matrix & Grid Operations",
        "task": "Filter agricultural hyperspectral NDVI vegetation indices for drought stress",
        "category": "Nested loop and complex conditional",
        "code": '''def detect_drought_stress_grid(
    nir_band: list[list[float]], red_band: list[list[float]], soil_moisture: list[list[float]]
) -> list[tuple[int, int]]:
    stress_points = []
    h = len(nir_band)
    w = len(nir_band[0])
    for r in range(h):
        for c in range(w):
            nir = nir_band[r][c]
            red = red_band[r][c]
            ndvi = (nir - red) / max(0.01, nir + red)
            moist = soil_moisture[r][c]
            c1 = ndvi < 0.25 and moist < 0.15 and nir > 0.1
            c2 = ndvi < 0.35 and moist < 0.10 and red > 0.2
            c3 = not (ndvi < 0.05 and moist > 0.5)
            if (c1 or c2) and c3 and nir > 0.0:
                stress_points.append((r, c))
    return stress_points

if __name__ == "__main__":
    nb = [[0.3, 0.4], [0.2, 0.1]]
    rb = [[0.2, 0.1], [0.15, 0.2]]
    sm = [[0.1, 0.3], [0.08, 0.05]]
    assert len(detect_drought_stress_grid(nb, rb, sm)) >= 1
'''
    },
    "P0242": {
        "domain": "String Processing & Text Analysis",
        "task": "Collate rhyme scheme phoneme endings in literary poem analysis",
        "category": "Nested loop and complex conditional",
        "code": '''def match_rhyme_candidate_tokens(
    strophe_a: list[str], strophe_b: list[str]
) -> list[tuple[str, str]]:
    rhymes = []
    for w1 in strophe_a:
        for w2 in strophe_b:
            c1 = w1[-3:] == w2[-3:] and len(w1) >= 4 and len(w2) >= 4 and w1 != w2
            c2 = w1[-2:] == w2[-2:] and w1[0] != w2[0] and len(w1) >= 3 and w1 != w2
            c3 = not (w1.endswith("ing") and w2.endswith("ing") and w1[:-3] == w2[:-3])
            if (c1 or c2) and c3 and not (w1.isdigit() or w2.isdigit()):
                rhymes.append((w1, w2))
    return rhymes

if __name__ == "__main__":
    assert len(match_rhyme_candidate_tokens(["bright", "moon"], ["night", "sun"])) == 1
'''
    },
    "P0243": {
        "domain": "Graph or Tree Traversal",
        "task": "Audit autonomous system BGP inter-domain routing path peering policies",
        "category": "Nested loop and complex conditional",
        "code": '''def evaluate_bgp_route_peering(
    routes_a: list[dict[str, any]], routes_b: list[dict[str, any]]
) -> list[tuple[int, int]]:
    peered = []
    for ra in routes_a:
        for rb in routes_b:
            med_diff = abs(ra.get("med", 0) - rb.get("med", 0))
            as_path_len = len(ra.get("as_path", [])) + len(rb.get("as_path", []))
            c1 = med_diff <= 10 and as_path_len <= 6 and ra.get("tier1") is True
            c2 = ra.get("community") == rb.get("community") and as_path_len <= 8
            if (c1 or c2) and not ra.get("flapping", False) and not rb.get("blackholed", False):
                peered.append((ra["as_num"], rb["as_num"]))
    return peered

if __name__ == "__main__":
    r1 = [{"as_num": 101, "med": 5, "as_path": [1, 2], "tier1": True, "flapping": False}]
    r2 = [{"as_num": 202, "med": 8, "as_path": [3], "blackholed": False}]
    assert len(evaluate_bgp_route_peering(r1, r2)) == 1
'''
    },
    "P0244": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Assign operating theater surgical teams under specialty equipment availability",
        "category": "Nested loop and complex conditional",
        "code": '''def allocate_surgical_theaters(
    procedures: list[dict[str, any]], theaters: list[dict[str, any]]
) -> list[dict[str, str]]:
    assignments = []
    for proc in procedures:
        for th in theaters:
            specialty_ok = proc.get("specialty") == th.get("specialty")
            duration_ok = proc.get("duration_hours", 2) <= th.get("available_hours", 8)
            sterile_ok = th.get("laminar_flow_active") is True
            c1 = specialty_ok and duration_ok and sterile_ok
            c2 = proc.get("is_emergency") is True and duration_ok and not th.get("occupied", False)
            if (c1 or c2) and not proc.get("scheduled", False):
                assignments.append({"proc_id": proc["id"], "theater_id": th["id"]})
                proc["scheduled"] = True
    return assignments

if __name__ == "__main__":
    p = [{"id": "SURG-1", "specialty": "CARDIAC", "duration_hours": 4, "scheduled": False}]
    t = [{"id": "OR-4", "specialty": "CARDIAC", "available_hours": 6, "laminar_flow_active": True}]
    assert len(allocate_surgical_theaters(p, t)) == 1
'''
    },

    # 8. ALL THREE TARGET ISSUES (6 programs: P0245 - P0250)
    "P0245": {
        "domain": "Numerical Computation",
        "task": "Molecular dynamics Lennard-Jones intermolecular pair simulation step",
        "category": "All three target issues",
        "code": '''import math

def simulate_lennard_jones_molecular_step(molecules: list[dict[str, float]], cutoff_radius: float) -> list[dict[str, float]]:
    n = len(molecules)
    for i in range(n):
        for j in range(n):
            if i != j:
                dist = math.sqrt((molecules[i]["x"] - molecules[j]["x"])**2 + (molecules[i]["y"] - molecules[j]["y"])**2) + 0.001
                lj_force = (48.0 * molecules[i]["epsilon"] * ((molecules[i]["sigma"]**12 / dist**13) - 0.5 * (molecules[i]["sigma"]**6 / dist**7))) + (0.015 * molecules[i]["mass"] * molecules[j]["mass"] / (dist**2))
                if ((dist < cutoff_radius and molecules[i]["mass"] > 20.0 and molecules[j]["mass"] > 20.0) or (dist < 0.2 and molecules[i].get("ionized") is True and not molecules[j].get("fixed", False))) and abs(lj_force) > 0.001:
                    molecules[i]["vx"] += (molecules[i]["x"] - molecules[j]["x"]) / dist * lj_force * 0.05
    return molecules

if __name__ == "__main__":
    mols = [{"x": 0.0, "y": 0.0, "vx": 0.0, "mass": 28.0, "epsilon": 1.0, "sigma": 0.3}, {"x": 0.4, "y": 0.0, "vx": 0.0, "mass": 28.0, "epsilon": 1.0, "sigma": 0.3}]
    res = simulate_lennard_jones_molecular_step(mols, 1.0)
    assert len(res) == 2
'''
    },
    "P0246": {
        "domain": "Matrix & Grid Operations",
        "task": "Radar cross-section backscatter matrix analysis for concealed object detection",
        "category": "All three target issues",
        "code": '''def analyze_radar_backscatter_mesh(radar_grid: list[list[dict[str, float]]], reference_db: float) -> list[tuple[int, int]]:
    detections = []
    for r, row in enumerate(radar_grid):
        for c, cell in enumerate(row):
            for ref_val in cell.get("polarimetric_returns", [reference_db]):
                rcs_ratio = ((cell["sigma_hh_db"] - cell["sigma_vv_db"]) * 1.65) + ((cell["sigma_hv_db"] - ref_val) * 0.75) - (cell.get("ground_clutter_db", 10.0) * 0.25) + (cell.get("dielectric_constant", 3.0) * 2.8)
                if ((rcs_ratio > 35.0 and cell.get("coherence_factor", 0.0) >= 0.75 and cell["sigma_hh_db"] > reference_db + 15.0) or (cell.get("metallic_signature") is True and rcs_ratio > 25.0 and not cell.get("multipath_ghost", False))) and not cell.get("sensor_blinded", False):
                    detections.append((r, c))
    return detections

if __name__ == "__main__":
    grid = [[{"sigma_hh_db": 40.0, "sigma_vv_db": 10.0, "sigma_hv_db": 20.0, "polarimetric_returns": [10.0], "coherence_factor": 0.85, "sensor_blinded": False}]]
    assert len(analyze_radar_backscatter_mesh(grid, 10.0)) == 1
'''
    },
    "P0247": {
        "domain": "Data Aggregation and Statistics",
        "task": "Aggregate metropolitan municipal water distribution pipe burst vulnerability",
        "category": "All three target issues",
        "code": '''def audit_water_mains_burst_risk(districts: list[dict[str, any]], hazard_ceiling: float) -> list[str]:
    vulnerable_pipes = []
    for dist in districts:
        for main_line in dist.get("mains", []):
            for segment in main_line.get("segments", []):
                burst_risk_index = ((segment.get("operating_pressure_psi", 60) - 50.0) * 1.85) + (segment.get("age_years", 10) * 1.45) - (segment.get("wall_thickness_mm", 10) * 3.2) + (segment.get("soil_corrosivity", 1.0) * 12.0)
                if ((burst_risk_index > hazard_ceiling and segment.get("is_cast_iron") is True and not dist.get("cathodic_protection_active", False)) or (segment.get("prior_leaks_count", 0) >= 3 and burst_risk_index > 50.0 and not segment.get("epoxy_lined", False))) and dist.get("active") is True:
                    vulnerable_pipes.append(segment["pipe_id"])
    return vulnerable_pipes

if __name__ == "__main__":
    d = [{"active": True, "cathodic_protection_active": False, "mains": [{"segments": [{"pipe_id": "P-99", "operating_pressure_psi": 120.0, "age_years": 60, "wall_thickness_mm": 6.0, "soil_corrosivity": 3.0, "is_cast_iron": True}]}]}]
    assert len(audit_water_mains_burst_risk(d, 80.0)) == 1
'''
    },
    "P0248": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Multi-tier satellite constellation ground station tracking downlink scheduler",
        "category": "All three target issues",
        "code": '''def schedule_satellite_downlink_passes(ground_stations: list[dict[str, any]], satellite_passes: list[dict[str, any]]) -> list[tuple[str, str]]:
    pass_schedule = []
    for gs in ground_stations:
        for antenna in gs.get("antennas", []):
            for sat_pass in satellite_passes:
                link_margin_db = (antenna.get("g_over_t_dbk", 25.0) * 1.15) + (sat_pass.get("eirp_dbw", 40.0) * 0.85) - (sat_pass.get("slant_range_km", 1000) * 0.012) - (gs.get("rain_attenuation_db", 1.0) * 1.5)
                if (not sat_pass.get("scheduled") and antenna.get("band") == sat_pass.get("req_band") and link_margin_db >= 6.0 and (gs.get("country") == sat_pass.get("allowed_country") or sat_pass.get("international_ok") is True)) and not antenna.get("maintenance", False):
                    pass_schedule.append((antenna["id"], sat_pass["id"]))
                    sat_pass["scheduled"] = True
    return pass_schedule

if __name__ == "__main__":
    gs_list = [{"country": "NO", "rain_attenuation_db": 0.5, "antennas": [{"id": "ANT-SVAL", "band": "X_BAND", "g_over_t_dbk": 30.0, "maintenance": False}]}]
    p_list = [{"id": "PASS-401", "req_band": "X_BAND", "eirp_dbw": 45.0, "slant_range_km": 800.0, "allowed_country": "NO", "international_ok": False, "scheduled": False}]
    assert len(schedule_satellite_downlink_passes(gs_list, p_list)) == 1
'''
    },
    "P0249": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Simulate natural gas pipeline compressor station surge and venting",
        "category": "All three target issues",
        "code": '''def simulate_gas_pipeline_surge_venting(compressor_stations: list[list[dict[str, any]]], automated_esd_armed: bool) -> list[dict[str, any]]:
    venting_events = []
    for corridor_idx, corridor in enumerate(compressor_stations):
        for station_idx, station in enumerate(corridor):
            for comp in station.get("compressor_units", []):
                surge_deviation_pct = (((comp["discharge_pressure_kpa"] / max(1.0, comp["suction_pressure_kpa"])) - comp["surge_line_ratio"]) * 100.0) + (comp["vibration_mms"] * 8.5) - (comp.get("recycle_valve_open_pct", 0) * 0.8)
                if ((surge_deviation_pct > 15.0 and comp.get("discharge_temp_c", 0) > 110.0 and not automated_esd_armed) or (comp.get("vibration_mms", 0) > 12.0 and comp.get("shaft_speed_rpm", 0) > 8000 and not station.get("bypassed", False))) and not comp.get("standby", False):
                    venting_events.append({"corridor": corridor_idx, "station": station_idx, "unit": comp["id"], "surge": surge_deviation_pct})
    return venting_events

if __name__ == "__main__":
    c_grid = [[{"bypassed": False, "compressor_units": [{"id": "C-1", "discharge_pressure_kpa": 6000.0, "suction_pressure_kpa": 2000.0, "surge_line_ratio": 2.2, "vibration_mms": 5.0, "discharge_temp_c": 125.0, "standby": False}]}]]
    assert len(simulate_gas_pipeline_surge_venting(c_grid, False)) == 1
'''
    },
    "P0250": {
        "domain": "Inventory and Record Management",
        "task": "Audit maritime cargo customs manifest risk against sanctioned transshipment hubs",
        "category": "All three target issues",
        "code": '''def audit_maritime_container_manifests(shipping_lines: list[dict[str, any]], sanctioned_ports: list[str]) -> list[dict[str, any]]:
    suspicious_cargo = []
    for line in shipping_lines:
        for vessel in line.get("vessels", []):
            for container in vessel.get("manifested_containers", []):
                customs_risk_index = ((container.get("declared_weight_kg", 0) / max(1.0, container.get("scanned_weight_kg", 1))) * 45.0) + (container.get("hs_code_dual_use_tier", 0) * 18.5) + (container.get("transshipment_hops", 0) * 12.0) - 25.0
                if ((customs_risk_index > 65.0 and container.get("origin_port") in sanctioned_ports and not container.get("pre_cleared_by_cbp", False)) or (container.get("declared_val_usd", 0) > 500000.0 and container.get("radiological_alarm") is True and not vessel.get("flag_of_convenience", False))) and not container.get("released", False):
                    suspicious_cargo.append({"vessel_imo": vessel["imo"], "container_id": container["id"], "risk": customs_risk_index})
    return suspicious_cargo

if __name__ == "__main__":
    lines = [{"vessels": [{"imo": 9876543, "flag_of_convenience": False, "manifested_containers": [{"id": "MSCU123", "declared_weight_kg": 25000, "scanned_weight_kg": 20000, "hs_code_dual_use_tier": 2, "transshipment_hops": 3, "origin_port": "PORT_XYZ", "pre_cleared_by_cbp": False, "released": False}]}]}]
    assert len(audit_maritime_container_manifests(lines, ["PORT_XYZ"])) == 1
'''
    }
}

def main():
    os.makedirs(PROGRAMS_DIR, exist_ok=True)
    written_count = 0
    new_rows = []

    for pid, data in sorted(PROGRAMS_DATA.items()):
        filename = f"{pid}.py"
        filepath = os.path.join(PROGRAMS_DIR, filename)
        code = data["code"].lstrip()

        # AST syntax parsing verification
        ast.parse(code)

        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        written_count += 1

        new_rows.append([
            pid,
            filename,
            data["domain"],
            data["task"],
            data["category"],
            MODEL_ID,
            PROMPT_VER,
            BATCH_ID,
            "True",
            "ACCEPTED"
        ])

    print(f"Generated and verified {written_count} program files (P0201-P0250).")

    # Append to manifest.csv
    with open(MANIFEST_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)

    print(f"Manifest successfully updated at: {MANIFEST_PATH}")

if __name__ == "__main__":
    main()