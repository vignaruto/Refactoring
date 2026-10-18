"""
expand_corpus_batch2.py
Automated script to generate P0051-P0100 and update program_corpus/manifest.csv
"""

import os
import ast
import csv
import hashlib

BASE_DIR = "program_corpus"
PROGRAMS_DIR = os.path.join(BASE_DIR, "programs")
MANIFEST_PATH = os.path.join(BASE_DIR, "manifest.csv")

MODEL_ID = "gemini-2.5-pro"
PROMPT_VER = "v2.0-expansion"
BATCH_ID = "Batch 2"

# ---------------------------------------------------------------------------
# Program Definitions (P0051 - P0100)
# ---------------------------------------------------------------------------
PROGRAMS_DATA = {
    # 1. NONE (8 programs: P0051 - P0058)
    "P0051": {
        "domain": "Numerical Computation",
        "task": "Extended Euclidean Algorithm for modular inverse",
        "category": "None",
        "code": '''import typing

def extended_gcd(a: int, b: int) -> tuple[int, int, int]:
    if a == 0:
        return b, 0, 1
    gcd, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd, x, y

def modular_inverse(base: int, modulus: int) -> typing.Optional[int]:
    gcd, x, _ = extended_gcd(base, modulus)
    if gcd != 1:
        return None
    return (x % modulus + modulus) % modulus

if __name__ == "__main__":
    assert modular_inverse(3, 11) == 4
'''
    },
    "P0052": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Run-length encoding of sequential items",
        "category": "None",
        "code": '''from typing import List, Tuple, Any

def run_length_encode(sequence: List[Any]) -> List[Tuple[Any, int]]:
    if not sequence:
        return []
    result = []
    current_val = sequence[0]
    count = 1
    for item in sequence[1:]:
        if item == current_val:
            count += 1
        else:
            result.append((current_val, count))
            current_val = item
            count = 1
    result.append((current_val, count))
    return result

if __name__ == "__main__":
    assert run_length_encode(["a", "a", "b"]) == [("a", 2), ("b", 1)]
'''
    },
    "P0053": {
        "domain": "String Processing & Text Analysis",
        "task": "Convert snake_case string to camelCase",
        "category": "None",
        "code": '''def snake_to_camel(identifier: str) -> str:
    tokens = identifier.strip().split("_")
    filtered = [token for token in tokens if token]
    if not filtered:
        return ""
    lead = filtered[0].lower()
    tail = [word.capitalize() for word in filtered[1:]]
    return lead + "".join(tail)

if __name__ == "__main__":
    assert snake_to_camel("order_unit_cost") == "orderUnitCost"
'''
    },
    "P0054": {
        "domain": "Searching and Sorting",
        "task": "Find peak element in 1D array using binary search",
        "category": "None",
        "code": '''from typing import List

def find_peak_element(nums: List[int]) -> int:
    left = 0
    right = len(nums) - 1
    while left < right:
        mid = (left + right) // 2
        if nums[mid] > nums[mid + 1]:
            right = mid
        else:
            left = mid + 1
    return left

if __name__ == "__main__":
    assert find_peak_element([1, 2, 3, 1]) == 2
'''
    },
    "P0055": {
        "domain": "Data Aggregation and Statistics",
        "task": "Compute exponential moving average of series",
        "category": "None",
        "code": '''from typing import List

def exponential_moving_average(series: List[float], alpha: float) -> List[float]:
    if not series:
        return []
    ema = [series[0]]
    for val in series[1:]:
        updated = alpha * val + (1.0 - alpha) * ema[-1]
        ema.append(round(updated, 4))
    return ema

if __name__ == "__main__":
    prices = [10.0, 11.0, 12.0, 11.5]
    res = exponential_moving_average(prices, 0.5)
    assert len(res) == 4
'''
    },
    "P0056": {
        "domain": "Inventory and Record Management",
        "task": "Calculate inventory reorder point using lead time demand",
        "category": "None",
        "code": '''from typing import Dict

def compute_reorder_level(item: Dict[str, float], safety_stock_ratio: float) -> float:
    daily_sales = item.get("avg_daily_sales", 0.0)
    lead_days = item.get("lead_time_days", 0.0)
    demand_during_lead = daily_sales * lead_days
    safety_buffer = demand_during_lead * safety_stock_ratio
    return demand_during_lead + safety_buffer

if __name__ == "__main__":
    prod = {"avg_daily_sales": 15.0, "lead_time_days": 10.0}
    assert compute_reorder_level(prod, 0.2) == 180.0
'''
    },
    "P0057": {
        "domain": "Graph or Tree Traversal",
        "task": "Count total leaf nodes in a binary tree representation",
        "category": "None",
        "code": '''from typing import Optional, Dict, Any

def count_leaf_nodes(node: Optional[Dict[str, Any]]) -> int:
    if node is None:
        return 0
    left_child = node.get("left")
    right_child = node.get("right")
    if left_child is None and right_child is None:
        return 1
    return count_leaf_nodes(left_child) + count_leaf_nodes(right_child)

if __name__ == "__main__":
    tree = {"left": {"left": None, "right": None}, "right": None}
    assert count_leaf_nodes(tree) == 1
'''
    },
    "P0058": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Simulate simple token bucket rate limiter single event",
        "category": "None",
        "code": '''from typing import Tuple

def consume_token(
    capacity: float, current_tokens: float,
    refill_rate: float, elapsed_sec: float
) -> Tuple[bool, float]:
    refilled = current_tokens + (elapsed_sec * refill_rate)
    pool = min(capacity, refilled)
    if pool >= 1.0:
        return True, pool - 1.0
    return False, pool

if __name__ == "__main__":
    allowed, tokens = consume_token(10.0, 0.5, 2.0, 1.0)
    assert allowed is True
    assert tokens == 1.5
'''
    },

    # 2. LONG STATEMENT ONLY (6 programs: P0059 - P0064)
    "P0059": {
        "domain": "Numerical Computation",
        "task": "Calculate geometric sphere cap volume and total surface area",
        "category": "Long statement only",
        "code": '''import math

def compute_spherical_cap_geometry(radius: float, cap_height: float, density: float) -> float:
    cap_mass = density * ((math.pi * (cap_height ** 2) / 3.0) * (3.0 * radius - cap_height)) + (2.0 * math.pi * radius * cap_height * 0.05)
    return cap_mass

if __name__ == "__main__":
    assert compute_spherical_cap_geometry(10.0, 2.0, 1.5) > 0.0
'''
    },
    "P0060": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Compute weighted asset allocation variance across portfolios",
        "category": "Long statement only",
        "code": '''from typing import Dict

def evaluate_multi_asset_portfolio_yield(equity: Dict[str, float], fixed_income: Dict[str, float], cash: Dict[str, float], base_tax: float) -> float:
    composite_return = (equity["yield"] * equity["weight"] * (1.0 - base_tax * 0.8)) + (fixed_income["yield"] * fixed_income["weight"] * (1.0 - base_tax)) + (cash["yield"] * cash["weight"] * (1.0 - base_tax * 0.5))
    return composite_return

if __name__ == "__main__":
    eq = {"yield": 0.12, "weight": 0.5}
    fi = {"yield": 0.06, "weight": 0.3}
    ca = {"yield": 0.03, "weight": 0.2}
    assert evaluate_multi_asset_portfolio_yield(eq, fi, ca, 0.15) > 0
'''
    },
    "P0061": {
        "domain": "Data Aggregation and Statistics",
        "task": "Calculate student composite academic honor score",
        "category": "Long statement only",
        "code": '''from typing import Dict

def compute_composite_honor_index(student: Dict[str, float], department_weight: float) -> float:
    honor_index = ((student["gpa"] * 25.0 * department_weight) + (student["research_units"] * 4.5) + (student["service_hours"] * 0.75) - (student["disciplinary_demerits"] * 12.0)) / (student["credits_completed"] * 0.1 + 1.0)
    return honor_index

if __name__ == "__main__":
    stu = {"gpa": 3.8, "research_units": 6.0, "service_hours": 40.0, "disciplinary_demerits": 0.0, "credits_completed": 90.0}
    assert compute_composite_honor_index(stu, 1.1) > 0.0
'''
    },
    "P0062": {
        "domain": "Inventory and Record Management",
        "task": "Compute corporate freight shipping tariff and insurance",
        "category": "Long statement only",
        "code": '''from typing import Dict

def calculate_freight_consignment_cost(parcel: Dict[str, float], distance_km: float, fuel_surcharge_rate: float) -> float:
    total_freight_charge = (parcel["weight_kg"] * 1.85 * (1.0 + fuel_surcharge_rate)) + (parcel["volume_cbm"] * 45.0) + (distance_km * 0.082) + (parcel["declared_value"] * 0.0075) + 25.0
    return total_freight_charge

if __name__ == "__main__":
    p = {"weight_kg": 50.0, "volume_cbm": 0.5, "declared_value": 1200.0}
    assert calculate_freight_consignment_cost(p, 300.0, 0.12) > 0.0
'''
    },
    "P0063": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Compute server datacenter power usage effectiveness overhead",
        "category": "Long statement only",
        "code": '''from typing import Dict

def compute_server_pue_overhead(telemetry: Dict[str, float], ambient_temp_c: float) -> float:
    adjusted_overhead_kw = (telemetry["cooling_kw"] * (1.0 + 0.02 * max(0.0, ambient_temp_c - 22.0))) + (telemetry["ups_loss_kw"] * 1.05) + (telemetry["lighting_kw"] * 0.95) + (telemetry["switchgear_loss_kw"] * 1.02)
    return adjusted_overhead_kw

if __name__ == "__main__":
    t = {"cooling_kw": 120.0, "ups_loss_kw": 15.0, "lighting_kw": 8.0, "switchgear_loss_kw": 5.0}
    assert compute_server_pue_overhead(t, 28.0) > 0.0
'''
    },
    "P0064": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Calculate aerodynamic drag and terminal settling velocity of aerosol",
        "category": "Long statement only",
        "code": '''import math
from typing import Dict

def aerosol_settling_terminal_velocity(particle: Dict[str, float], medium_viscosity: float, gravity: float = 9.80665) -> float:
    return ((2.0 * (particle["radius_m"] ** 2) * (particle["density_kg_m3"] - particle["medium_density_kg_m3"]) * gravity) / (9.0 * medium_viscosity)) * (1.0 + (1.257 * 68e-9 / particle["radius_m"]))

if __name__ == "__main__":
    part = {"radius_m": 2.5e-6, "density_kg_m3": 1200.0, "medium_density_kg_m3": 1.2}
    assert aerosol_settling_terminal_velocity(part, 1.81e-5) > 0.0
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0065 - P0070)
    "P0065": {
        "domain": "Numerical Computation",
        "task": "Compute pairwise Minkowski distance matrix between vector collections",
        "category": "Nested loop only",
        "code": '''from typing import List

def pairwise_minkowski_distances(
    vecs_a: List[List[float]],
    vecs_b: List[List[float]],
    p: int
) -> List[List[float]]:
    dist_matrix = []
    for u in vecs_a:
        row = []
        for v in vecs_b:
            diff_sum = 0.0
            for k in range(len(u)):
                diff_sum += abs(u[k] - v[k]) ** p
            row.append(diff_sum ** (1.0 / p))
        dist_matrix.append(row)
    return dist_matrix

if __name__ == "__main__":
    a = [[1.0, 2.0]]
    b = [[4.0, 6.0]]
    assert len(pairwise_minkowski_distances(a, b, 2)) == 1
'''
    },
    "P0066": {
        "domain": "Searching and Sorting",
        "task": "Perform shell sort with custom interval sequences",
        "category": "Nested loop only",
        "code": '''from typing import List

def shell_sort_integers(items: List[int]) -> List[int]:
    arr = list(items)
    n = len(arr)
    gap = n // 2
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2
    return arr

if __name__ == "__main__":
    assert shell_sort_integers([9, 8, 3, 7, 5, 6, 4, 1]) == [1, 3, 4, 5, 6, 7, 8, 9]
'''
    },
    "P0067": {
        "domain": "Matrix & Grid Operations",
        "task": "Transposing a block partitioned 2D matrix",
        "category": "Nested loop only",
        "code": '''from typing import List

def transpose_matrix(matrix: List[List[float]]) -> List[List[float]]:
    rows = len(matrix)
    cols = len(matrix[0])
    transposed = []
    for c in range(cols):
        new_row = []
        for r in range(rows):
            val = matrix[r][c]
            new_row.append(val)
        transposed.append(new_row)
    return transposed

if __name__ == "__main__":
    m = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]
    t = transpose_matrix(m)
    assert len(t) == 3
    assert len(t[0]) == 2
'''
    },
    "P0068": {
        "domain": "String Processing & Text Analysis",
        "task": "Find all common substrings between two word lists",
        "category": "Nested loop only",
        "code": '''from typing import List, Set

def find_common_word_ngrams(words_a: List[str], words_b: List[str]) -> Set[str]:
    common = set()
    for word_1 in words_a:
        for word_2 in words_b:
            len_min = min(len(word_1), len(word_2))
            for k in range(3, len_min + 1):
                sub = word_1[:k]
                if sub in word_2:
                    common.add(sub)
    return common

if __name__ == "__main__":
    res = find_common_word_ngrams(["transformation", "reform"], ["transfer", "formation"])
    assert "trans" in res or "form" in res
'''
    },
    "P0069": {
        "domain": "Graph or Tree Traversal",
        "task": "Floyd-Warshall all-pairs shortest paths algorithm",
        "category": "Nested loop only",
        "code": '''from typing import List

def floyd_warshall(weights: List[List[float]]) -> List[List[float]]:
    n = len(weights)
    dist = [row[:] for row in weights]
    for k in range(n):
        for i in range(n):
            for j in range(n):
                cand = dist[i][k] + dist[k][j]
                if cand < dist[i][j]:
                    dist[i][j] = cand
    return dist

if __name__ == "__main__":
    inf = float("inf")
    w = [[0.0, 5.0, inf], [inf, 0.0, 2.0], [inf, inf, 0.0]]
    d = floyd_warshall(w)
    assert d[0][2] == 7.0
'''
    },
    "P0070": {
        "domain": "Inventory and Record Management",
        "task": "Count co-occurring items across customer transaction baskets",
        "category": "Nested loop only",
        "code": '''from typing import List, Dict, Tuple

def generate_item_pair_frequencies(baskets: List[List[str]]) -> Dict[Tuple[str, str], int]:
    pair_counts = {}
    for basket in baskets:
        sorted_items = sorted(basket)
        for i in range(len(sorted_items)):
            for j in range(i + 1, len(sorted_items)):
                pair = (sorted_items[i], sorted_items[j])
                current = pair_counts.get(pair, 0)
                pair_counts[pair] = current + 1
    return pair_counts

if __name__ == "__main__":
    sample = [["milk", "bread", "eggs"], ["milk", "bread"]]
    counts = generate_item_pair_frequencies(sample)
    assert counts[("bread", "milk")] == 2
'''
    },

    # 4. COMPLEX CONDITIONAL ONLY (6 programs: P0071 - P0076)
    "P0071": {
        "domain": "Numerical Computation",
        "task": "Validate parameters for numerical integration stability",
        "category": "Complex conditional only",
        "code": '''def is_solver_step_valid(step_size: float, tolerance: float, stiffness_ratio: float, order: int) -> bool:
    cond1 = step_size > 0.0 and step_size < 0.5 and tolerance <= 1e-4
    cond2 = stiffness_ratio > 100.0 and order >= 2 and tolerance > 1e-7
    cond3 = order == 1 and step_size <= 0.01 and not stiffness_ratio > 500.0
    if (cond1 or cond2) and not cond3 and (stiffness_ratio < 1000.0 or order > 3):
        return True
    return False

if __name__ == "__main__":
    assert is_solver_step_valid(0.05, 1e-5, 150.0, 3) is True
'''
    },
    "P0072": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Filter authorized network sessions based on security posture",
        "category": "Complex conditional only",
        "code": '''from typing import Dict

def is_network_session_authorized(
    session: Dict[str, any], client: Dict[str, any], gateway_secure: bool
) -> bool:
    is_tls = session.get("tls_version", 0.0) >= 1.3
    cert_ok = client.get("cert_valid") is True
    ip_white = client.get("whitelisted_ip") is True
    mfa_done = session.get("mfa_verified") is True
    revoked = client.get("cert_revoked") is True
    if (is_tls and cert_ok and ip_white) or (
        mfa_done and gateway_secure and not revoked
    ):
        return True
    return False

if __name__ == "__main__":
    s = {"tls_version": 1.3, "mfa_verified": False}
    c = {"cert_valid": True, "whitelisted_ip": True, "cert_revoked": False}
    assert is_network_session_authorized(s, c, True) is True
'''
    },
    "P0073": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate complex password policy conformance",
        "category": "Complex conditional only",
        "code": '''def evaluate_password_policy(pwd: str, has_special: bool, entropy_bits: float) -> bool:
    has_len = len(pwd) >= 12 and len(pwd) <= 64
    has_upper = any(c.isupper() for c in pwd)
    has_digit = any(c.isdigit() for c in pwd)
    if (has_len and has_upper and has_digit and has_special) or (
        len(pwd) >= 20 and entropy_bits >= 75.0 and not " " in pwd
    ):
        return True
    return False

if __name__ == "__main__":
    assert evaluate_password_policy("SecureP@ssword123", True, 60.0) is True
'''
    },
    "P0074": {
        "domain": "Data Aggregation and Statistics",
        "task": "Classify clinical trial participant eligibility",
        "category": "Complex conditional only",
        "code": '''from typing import Dict

def is_candidate_eligible(patient: Dict[str, float], consent_signed: bool) -> bool:
    age = patient.get("age", 0.0)
    bmi = patient.get("bmi", 0.0)
    bp = patient.get("systolic_bp", 0.0)
    hba1c = patient.get("hba1c", 0.0)
    cond_a = age >= 18.0 and age <= 65.0 and bmi < 32.0 and bp < 140.0
    cond_b = age > 65.0 and hba1c < 6.5 and bp < 130.0
    if (cond_a or cond_b) and consent_signed and not patient.get("pregnant", False):
        return True
    return False

if __name__ == "__main__":
    pat = {"age": 45.0, "bmi": 26.0, "systolic_bp": 125.0, "pregnant": False}
    assert is_candidate_eligible(pat, True) is True
'''
    },
    "P0075": {
        "domain": "Inventory and Record Management",
        "task": "Automated warehouse refund approval authorization",
        "category": "Complex conditional only",
        "code": '''from typing import Dict

def can_auto_approve_refund(
    order: Dict[str, any], item: Dict[str, any], days_since_delivery: int
) -> bool:
    is_prime = order.get("member_tier") == "prime"
    cost = item.get("unit_price", 0.0)
    unopened = item.get("sealed_box") is True
    has_dispute = order.get("open_disputes", 0) > 0
    fraud_score = order.get("fraud_score", 0.0)
    rule1 = days_since_delivery <= 30 and unopened and cost <= 250.0
    rule2 = is_prime and days_since_delivery <= 45 and cost <= 100.0
    if (rule1 or rule2) and not has_dispute and fraud_score < 0.15:
        return True
    return False

if __name__ == "__main__":
    o = {"member_tier": "prime", "open_disputes": 0, "fraud_score": 0.05}
    it = {"unit_price": 80.0, "sealed_box": False}
    assert can_auto_approve_refund(o, it, 20) is True
'''
    },
    "P0076": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Determine autonomous vehicle dispatch safety clearance",
        "category": "Complex conditional only",
        "code": '''from typing import Dict

def is_dispatch_permitted(
    vehicle: Dict[str, float], weather: Dict[str, float], emergency_mode: bool
) -> bool:
    soc = vehicle.get("battery_soc", 0.0)
    tire = vehicle.get("tire_health", 0.0)
    vis = weather.get("visibility_km", 0.0)
    ice = weather.get("road_ice_warning", False)
    cond1 = soc >= 0.35 and tire >= 0.80 and vis >= 2.0
    cond2 = emergency_mode and soc >= 0.20 and not ice
    if (cond1 or cond2) and not vehicle.get("fault_codes_active", False) and weather.get("wind_gust_kph", 0.0) < 70.0:
        return True
    return False

if __name__ == "__main__":
    veh = {"battery_soc": 0.6, "tire_health": 0.9, "fault_codes_active": False}
    w = {"visibility_km": 5.0, "road_ice_warning": False, "wind_gust_kph": 30.0}
    assert is_dispatch_permitted(veh, w, False) is True
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (6 programs: P0077 - P0082)
    "P0077": {
        "domain": "Numerical Computation",
        "task": "Bilinear surface interpolation across 2D grid coordinates",
        "category": "Long statement and nested loop",
        "code": '''from typing import List

def bilinear_grid_interpolation(grid: List[List[float]], x_coords: List[float], y_coords: List[float]) -> List[List[float]]:
    output = []
    for x in x_coords:
        row = []
        for y in y_coords:
            x1, y1 = int(x), int(y)
            x2, y2 = min(x1 + 1, len(grid) - 1), min(y1 + 1, len(grid[0]) - 1)
            val = (grid[x1][y1] * (x2 - x) * (y2 - y)) + (grid[x2][y1] * (x - x1) * (y2 - y)) + (grid[x1][y2] * (x2 - x) * (y - y1)) + (grid[x2][y2] * (x - x1) * (y - y1))
            row.append(val)
        output.append(row)
    return output

if __name__ == "__main__":
    g = [[1.0, 2.0], [3.0, 4.0]]
    res = bilinear_grid_interpolation(g, [0.5], [0.5])
    assert len(res) == 1
'''
    },
    "P0078": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Aggregate multi-source sensor measurements with spatial weighting",
        "category": "Long statement and nested loop",
        "code": '''import math
from typing import List, Dict

def compute_spatial_sensor_influence(stations: List[Dict[str, float]], probes: List[Dict[str, float]], decay_rate: float) -> List[float]:
    influences = []
    for probe in probes:
        acc = 0.0
        for station in stations:
            acc += station["power"] / (1.0 + decay_rate * math.sqrt((station["x"] - probe["x"])**2 + (station["y"] - probe["y"])**2 + (station["z"] - probe["z"])**2))
        influences.append(acc)
    return influences

if __name__ == "__main__":
    st = [{"power": 100.0, "x": 0.0, "y": 0.0, "z": 0.0}]
    pr = [{"x": 3.0, "y": 4.0, "z": 0.0}]
    assert len(compute_spatial_sensor_influence(st, pr, 0.1)) == 1
'''
    },
    "P0079": {
        "domain": "Matrix & Grid Operations",
        "task": "Convolution kernel filtering with normalization",
        "category": "Long statement and nested loop",
        "code": '''from typing import List

def apply_blur_filter(image: List[List[float]], kernel_weights: List[List[float]], divisor: float) -> List[List[float]]:
    h, w = len(image), len(image[0])
    filtered = [[0.0] * w for _ in range(h)]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            filtered[r][c] = (image[r-1][c-1]*kernel_weights[0][0] + image[r-1][c]*kernel_weights[0][1] + image[r-1][c+1]*kernel_weights[0][2] + image[r][c-1]*kernel_weights[1][0] + image[r][c]*kernel_weights[1][1] + image[r][c+1]*kernel_weights[1][2] + image[r+1][c-1]*kernel_weights[2][0] + image[r+1][c]*kernel_weights[2][1] + image[r+1][c+1]*kernel_weights[2][2]) / divisor
    return filtered

if __name__ == "__main__":
    img = [[1.0]*3 for _ in range(3)]
    k = [[1.0]*3 for _ in range(3)]
    assert apply_blur_filter(img, k, 9.0)[1][1] == 1.0
'''
    },
    "P0080": {
        "domain": "Data Aggregation and Statistics",
        "task": "Compute pairwise covariance and correlation across multi-asset returns",
        "category": "Long statement and nested loop",
        "code": '''from typing import List

def compute_asset_covariance_table(asset_returns: List[List[float]], means: List[float]) -> List[List[float]]:
    n = len(asset_returns)
    samples = len(asset_returns[0])
    table = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            table[i][j] = sum((asset_returns[i][t] - means[i]) * (asset_returns[j][t] - means[j]) for t in range(samples)) / float(samples - 1.0)
    return table

if __name__ == "__main__":
    rets = [[0.01, 0.02, 0.03], [0.02, 0.01, 0.04]]
    means = [0.02, 0.0233]
    res = compute_asset_covariance_table(rets, means)
    assert len(res) == 2
'''
    },
    "P0081": {
        "domain": "Searching and Sorting",
        "task": "Find optimal rectangular subgrid with minimum variance",
        "category": "Long statement and nested loop",
        "code": '''from typing import List, Tuple

def locate_least_variant_patch(grid: List[List[float]], size: int) -> Tuple[int, int]:
    h = len(grid) - size + 1
    w = len(grid[0]) - size + 1
    best_loc = (0, 0)
    min_variance = float("inf")
    for r in range(h):
        for c in range(w):
            patch_var = sum((grid[r + dr][c + dc] - 50.0)**2 for dr in range(size) for dc in range(size)) / float(size * size)
            if patch_var < min_variance:
                min_variance = patch_var
                best_loc = (r, c)
    return best_loc

if __name__ == "__main__":
    g = [[50.0]*4 for _ in range(4)]
    assert locate_least_variant_patch(g, 2) == (0, 0)
'''
    },
    "P0082": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Compute multi-phase job execution latencies across processor nodes",
        "category": "Long statement and nested loop",
        "code": '''from typing import List, Dict

def compute_processor_task_delays(nodes: List[Dict[str, float]], tasks: List[Dict[str, float]], network_overhead: float) -> List[List[float]]:
    latencies = []
    for node in nodes:
        row = []
        for task in tasks:
            turnaround_time = (task["payload_mb"] / node["bandwidth_mbps"]) + (task["cycles_giga"] / node["clock_ghz"] * node["ipc_efficiency"]) + network_overhead
            row.append(turnaround_time)
        latencies.append(row)
    return latencies

if __name__ == "__main__":
    n = [{"bandwidth_mbps": 100.0, "clock_ghz": 3.0, "ipc_efficiency": 1.2}]
    t = [{"payload_mb": 50.0, "cycles_giga": 6.0}]
    assert len(compute_processor_task_delays(n, t, 0.05)) == 1
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0083 - P0088)
    "P0083": {
        "domain": "Numerical Computation",
        "task": "Evaluate atmospheric flight path aerodynamic coefficients",
        "category": "Long statement and complex conditional",
        "code": '''import math
from typing import Dict

def evaluate_reentry_aerodynamics(state: Dict[str, float], thermal_shield_active: bool) -> float:
    alt = state.get("altitude_km", 0.0)
    mach = state.get("mach_number", 0.0)
    aoa = state.get("angle_of_attack_deg", 0.0)
    drag_force = 0.5 * state["air_density"] * (state["velocity_ms"] ** 2) * state["reference_area"] * (state["base_cd"] + 0.015 * (aoa ** 1.8) + 0.08 * math.exp(-alt / 8.5))
    if ((alt < 80.0 and mach > 5.0 and aoa <= 25.0) or (alt < 40.0 and state.get("plasma_blackout") is True)) and thermal_shield_active and not state.get("surface_damaged", False):
        return drag_force
    return 0.0

if __name__ == "__main__":
    s = {"altitude_km": 50.0, "mach_number": 12.0, "angle_of_attack_deg": 15.0, "air_density": 0.001, "velocity_ms": 4000.0, "reference_area": 12.0, "base_cd": 0.4}
    assert evaluate_reentry_aerodynamics(s, True) > 0.0
'''
    },
    "P0084": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Calculate commercial credit limit based on financial health indices",
        "category": "Long statement and complex conditional",
        "code": '''from typing import Dict

def evaluate_corporate_credit_facility(firm: Dict[str, float], sector_risk: float, audit_approved: bool) -> float:
    ratio_curr = firm.get("current_assets", 0.0) / (firm.get("current_liabilities", 1.0) + 1.0)
    ebitda = firm.get("ebitda", 0.0)
    debt_service = firm.get("debt_service", 1.0)
    credit_limit = (ebitda * 3.5 * (1.0 - sector_risk * 0.4)) + (firm.get("collateral_market_value", 0.0) * 0.65) - (firm.get("existing_debt", 0.0) * 0.35)
    if (ratio_curr >= 1.5 and ebitda / debt_service >= 2.5 and sector_risk <= 0.30) or (audit_approved and firm.get("tenure_years", 0.0) >= 10.0 and not firm.get("prior_defaults", False)):
        return max(0.0, credit_limit)
    return 0.0

if __name__ == "__main__":
    f = {"current_assets": 300.0, "current_liabilities": 100.0, "ebitda": 50.0, "debt_service": 10.0, "collateral_market_value": 200.0, "existing_debt": 40.0}
    assert evaluate_corporate_credit_facility(f, 0.2, True) > 0.0
'''
    },
    "P0085": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate and score complex URI endpoints for security gateways",
        "category": "Long statement and complex conditional",
        "code": '''def audit_endpoint_url_security(url: str, allowed_host: str, require_https: bool) -> float:
    token_complexity = (len(url) * 0.45) + (sum(c.isupper() for c in url) * 1.8) + (sum(c.isdigit() for c in url) * 1.2) - (url.count("/") * 2.5) + 10.0
    if (url.startswith("https://") and allowed_host in url and not ".." in url and len(url) <= 512) or (not require_https and url.startswith("http://localhost") and not "@" in url):
        return token_complexity
    return -1.0

if __name__ == "__main__":
    assert audit_endpoint_url_security("https://api.internal.com/v1/auth", "api.internal.com", True) > 0.0
'''
    },
    "P0086": {
        "domain": "Data Aggregation and Statistics",
        "task": "Compute demographic health risk score for epidemiological survey",
        "category": "Long statement and complex conditional",
        "code": '''from typing import Dict

def compute_epidemiological_vulnerability(subject: Dict[str, float], base_prevalence: float) -> float:
    vulnerability_score = (subject["age"] * 0.28) + (subject["bmi"] * 0.45) + (subject["blood_sugar"] * 0.15) + (subject["smoking_pack_years"] * 1.85) - (subject["physical_activity_hours_week"] * 3.5) + base_prevalence * 100.0
    if (subject.get("age", 0.0) >= 60.0 and subject.get("bmi", 0.0) >= 30.0 and subject.get("hypertension") is True) or (subject.get("immunocompromised") is True and base_prevalence >= 0.05 and not subject.get("vaccinated", False)):
        return vulnerability_score * 1.4
    return vulnerability_score

if __name__ == "__main__":
    sub = {"age": 65.0, "bmi": 32.0, "blood_sugar": 110.0, "smoking_pack_years": 10.0, "physical_activity_hours_week": 2.0, "hypertension": True}
    assert compute_epidemiological_vulnerability(sub, 0.02) > 0.0
'''
    },
    "P0087": {
        "domain": "Inventory and Record Management",
        "task": "Calculate pharmaceutical shelf expiry loss and inventory write-off",
        "category": "Long statement and complex conditional",
        "code": '''from typing import Dict

def calculate_pharma_spoilage_writeoff(batch: Dict[str, float], market_salvage_rate: float, emergency_cleared: bool) -> float:
    total_writeoff_loss = (batch["unit_cost"] * batch["units_expired"]) - (batch["units_expired"] * batch["unit_cost"] * market_salvage_rate) + (batch.get("hazmat_disposal_fee_per_unit", 2.5) * batch["units_expired"]) + 50.0
    if ((batch.get("units_expired", 0.0) > 100.0 and batch.get("is_controlled_substance") is True and not batch.get("quarantined", False)) or (batch.get("temperature_violation_hours", 0.0) > 24.0 and not emergency_cleared)) and batch.get("insurance_covered") is not True:
        return total_writeoff_loss
    return 0.0

if __name__ == "__main__":
    b = {"unit_cost": 25.0, "units_expired": 150.0, "is_controlled_substance": True, "quarantined": False, "insurance_covered": False}
    assert calculate_pharma_spoilage_writeoff(b, 0.1, False) > 0.0
'''
    },
    "P0088": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Simulate boiler steam pressure regulator and emergency blowout",
        "category": "Long statement and complex conditional",
        "code": '''from typing import Dict

def regulate_boiler_steam_chamber(boiler: Dict[str, float], ambient_pressure_psi: float) -> float:
    vent_flow_rate = (boiler["pressure_psi"] - ambient_pressure_psi) * boiler["orifice_area_sq_in"] * (0.62 + 0.0012 * (boiler["temperature_c"] - 100.0)) * 14.7
    if ((boiler.get("pressure_psi", 0.0) > 250.0 and boiler.get("temperature_c", 0.0) > 350.0 and boiler.get("water_level_pct", 0.0) < 15.0) or (boiler.get("pressure_psi", 0.0) > 300.0 and not boiler.get("backup_pump_running", False))) and not boiler.get("manual_scram_triggered", False):
        return vent_flow_rate
    return 0.0

if __name__ == "__main__":
    boil = {"pressure_psi": 280.0, "temperature_c": 380.0, "water_level_pct": 10.0, "orifice_area_sq_in": 1.5, "backup_pump_running": False, "manual_scram_triggered": False}
    assert regulate_boiler_steam_chamber(boil, 14.7) > 0.0
'''
    },

    # 7. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0089 - P0094)
    "P0089": {
        "domain": "Numerical Computation",
        "task": "Search constrained parameter space for stable differential roots",
        "category": "Nested loop and complex conditional",
        "code": '''from typing import List, Tuple

def locate_stable_roots_grid(
    grid_x: List[float], grid_y: List[float], damp: float
) -> List[Tuple[float, float]]:
    stable = []
    for x in grid_x:
        for y in grid_y:
            z = x**2 - y**2 + damp
            cond_a = z > 0.0 and x > 1.0 and y > 1.0
            cond_b = damp < 0.5 and z < 10.0 and x < 5.0
            cond_c = not (x == y and damp == 0.0)
            cond_d = (z != 1.0 or damp > 0.1)
            if (cond_a or cond_b) and cond_c and cond_d:
                stable.append((x, y))
    return stable

if __name__ == "__main__":
    assert len(locate_stable_roots_grid([2.0], [1.5], 0.2)) == 1
'''
    },
    "P0090": {
        "domain": "Searching and Sorting",
        "task": "Filter matching candidate profiles against multi-criteria job requisitions",
        "category": "Nested loop and complex conditional",
        "code": '''from typing import List, Dict

def match_candidates_to_roles(
    roles: List[Dict[str, any]],
    candidates: List[Dict[str, any]]
) -> List[Dict[str, str]]:
    matches = []
    for role in roles:
        for cand in candidates:
            exp_ok = cand.get("years_exp", 0) >= role.get("min_exp", 0)
            deg_ok = cand.get("degree") == role.get("req_degree")
            loc_ok = cand.get("location") == role.get("location")
            remote = role.get("remote_ok") is True
            sal_ok = cand.get("expected_sal", 0) <= role.get("max_sal", 0)
            rule_std = exp_ok and sal_ok and (loc_ok or remote)
            rule_vet = deg_ok and exp_ok and cand.get("veteran") is True
            if rule_std or rule_vet:
                matches.append({"role_id": role["id"], "cand_id": cand["id"]})
    return matches

if __name__ == "__main__":
    r = [{"id": "R1", "min_exp": 3, "location": "NY", "remote_ok": True, "max_sal": 100000}]
    c = [{"id": "C1", "years_exp": 4, "location": "SF", "expected_sal": 90000}]
    assert len(match_candidates_to_roles(r, c)) == 1
'''
    },
    "P0091": {
        "domain": "Matrix & Grid Operations",
        "task": "Scan grid matrix for anomalous local minimum clusters",
        "category": "Nested loop and complex conditional",
        "code": '''from typing import List, Tuple

def locate_anomalous_pits(matrix: List[List[float]], threshold: float) -> List[Tuple[int, int]]:
    pits = []
    rows = len(matrix)
    cols = len(matrix[0])
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            val = matrix[r][c]
            lower_h = val < matrix[r-1][c] and val < matrix[r+1][c]
            lower_v = val < matrix[r][c-1] and val < matrix[r][c+1]
            deep = val < threshold
            pit_a = lower_h and lower_v and deep
            pit_b = val < 0.0 and matrix[r-1][c-1] > threshold and not val == threshold
            if pit_a or pit_b:
                pits.append((r, c))
    return pits

if __name__ == "__main__":
    m = [[5.0, 5.0, 5.0], [5.0, 1.0, 5.0], [5.0, 5.0, 5.0]]
    assert locate_anomalous_pits(m, 2.0) == [(1, 1)]
'''
    },
    "P0092": {
        "domain": "String Processing & Text Analysis",
        "task": "Cross-compare document token pairs with multi-attribute filtering",
        "category": "Nested loop and complex conditional",
        "code": '''from typing import List, Tuple

def filter_cross_document_keyword_pairs(
    doc_a: List[str], doc_b: List[str], min_overlap_char: int
) -> List[Tuple[str, str]]:
    pairs = []
    for word_a in doc_a:
        for word_b in doc_b:
            shared = len(set(word_a).intersection(set(word_b)))
            len_diff = abs(len(word_a) - len(word_b))
            pair_a = shared >= min_overlap_char and len_diff <= 2 and word_a[0] == word_b[0]
            pair_b = word_a in word_b and len(word_a) >= 4 and not word_a == word_b
            if (pair_a or pair_b) and not word_a.isdigit():
                pairs.append((word_a, word_b))
    return pairs

if __name__ == "__main__":
    assert len(filter_cross_document_keyword_pairs(["cloud"], ["clouds"], 4)) == 1
'''
    },
    "P0093": {
        "domain": "Graph or Tree Traversal",
        "task": "Validate clustered server graph communication link rules",
        "category": "Nested loop and complex conditional",
        "code": '''from typing import Dict, List, Tuple

def audit_cluster_interlinks(cluster_a: Dict[str, any], cluster_b: Dict[str, any]) -> List[Tuple[str, str]]:
    valid_links = []
    nodes_a = cluster_a.get("nodes", [])
    nodes_b = cluster_b.get("nodes", [])
    for na in nodes_a:
        for nb in nodes_b:
            lat = na.get("latency_to_gw", 100) + nb.get("latency_to_gw", 100)
            bw = min(na.get("bandwidth", 0), nb.get("bandwidth", 0))
            link_a = lat <= 50 and bw >= 1000 and na.get("zone") == nb.get("zone")
            link_b = na.get("public_ip") is True and nb.get("vpc_peered") is True and lat <= 80
            if (link_a or link_b) and not na.get("draining", False):
                valid_links.append((na["id"], nb["id"]))
    return valid_links

if __name__ == "__main__":
    ca = {"nodes": [{"id": "A1", "latency_to_gw": 20, "bandwidth": 1500, "zone": "us-1", "draining": False}]}
    cb = {"nodes": [{"id": "B1", "latency_to_gw": 20, "bandwidth": 1500, "zone": "us-1"}]}
    assert len(audit_cluster_interlinks(ca, cb)) == 1
'''
    },
    "P0094": {
        "domain": "Inventory and Record Management",
        "task": "Reconcile supplier purchase orders across warehouse shipments",
        "category": "Nested loop and complex conditional",
        "code": '''from typing import List, Dict, Tuple

def reconcile_po_shipments(
    purchase_orders: List[Dict[str, any]],
    receipts: List[Dict[str, any]]
) -> List[Tuple[str, str]]:
    matched = []
    for po in purchase_orders:
        for rec in receipts:
            sku_match = po.get("sku") == rec.get("sku")
            qty_diff = abs(po.get("qty", 0) - rec.get("qty", 0))
            price_diff = abs(po.get("unit_price", 0.0) - rec.get("unit_price", 0.0))
            full_match = sku_match and qty_diff <= 2 and price_diff < 0.05 and not rec.get("damaged", False)
            part_match = sku_match and po.get("allow_partial") is True and rec.get("qty", 0) > 0 and not rec.get("inspected") is False
            if full_match or part_match:
                matched.append((po["po_id"], rec["rec_id"]))
    return matched

if __name__ == "__main__":
    pos = [{"po_id": "PO1", "sku": "SKU1", "qty": 100, "unit_price": 5.0, "allow_partial": False}]
    recs = [{"rec_id": "R1", "sku": "SKU1", "qty": 100, "unit_price": 5.0, "damaged": False}]
    assert len(reconcile_po_shipments(pos, recs)) == 1
'''
    },

    # 8. ALL THREE TARGET ISSUES (6 programs: P0095 - P0100)
    "P0095": {
        "domain": "Numerical Computation",
        "task": "N-body gravitation simulation step with multi-condition collision damping",
        "category": "All three target issues",
        "code": '''import math
from typing import List, Dict

def simulate_n_body_potential_step(bodies: List[Dict[str, float]], g_constant: float, damping_limit: float) -> List[Dict[str, float]]:
    n = len(bodies)
    for i in range(n):
        for j in range(n):
            if i != j:
                dx = bodies[j]["x"] - bodies[i]["x"]
                dy = bodies[j]["y"] - bodies[i]["y"]
                dist = math.sqrt(dx**2 + dy**2) + 0.001
                force_magnitude = (g_constant * bodies[i]["mass"] * bodies[j]["mass"]) / (dist ** 2) * (1.0 + 0.02 * (bodies[i].get("charge", 0.0) * bodies[j].get("charge", 0.0)))
                if ((dist < damping_limit and bodies[i]["mass"] > 100.0 and bodies[j]["mass"] > 100.0) or (dist < 0.05 and bodies[i].get("ionized") is True and not bodies[j].get("fixed", False))) and force_magnitude > 0.1:
                    bodies[i]["vx"] += (dx / dist) * force_magnitude * 0.1 / bodies[i]["mass"]
    return bodies

if __name__ == "__main__":
    b = [{"x": 0.0, "y": 0.0, "mass": 500.0, "vx": 0.0, "charge": 1.0, "ionized": True}, {"x": 1.0, "y": 0.0, "mass": 500.0, "vx": 0.0, "charge": 1.0, "fixed": False}]
    assert len(simulate_n_body_potential_step(b, 6.67e-11, 2.0)) == 2
'''
    },
    "P0096": {
        "domain": "Matrix & Grid Operations",
        "task": "Process multi-spectral satellite imagery raster tiles with radiometric calibration",
        "category": "All three target issues",
        "code": '''from typing import List, Dict, Tuple

def calibrate_satellite_raster_bands(tiles: List[List[Dict[str, float]]], solar_zenith_deg: float) -> List[Tuple[int, int]]:
    anomalies = []
    for r, row in enumerate(tiles):
        for c, pixel in enumerate(row):
            toa_reflectance = (pixel["digital_number"] * pixel["gain"] + pixel["bias"]) / (pixel["solar_irradiance"] * 0.95 * (1.0 + 0.033 * (solar_zenith_deg / 90.0)))
            if ((toa_reflectance > 0.85 and pixel.get("cloud_mask") == 0.0 and pixel.get("thermal_kelvin", 0.0) < 260.0) or (toa_reflectance < 0.02 and pixel.get("water_body") is True and not pixel.get("glint_flag", False))) and pixel.get("quality_flag", 1) == 1:
                anomalies.append((r, c))
    return anomalies

if __name__ == "__main__":
    grid = [[{"digital_number": 200.0, "gain": 0.005, "bias": 0.1, "solar_irradiance": 1.5, "cloud_mask": 0.0, "thermal_kelvin": 250.0, "quality_flag": 1}]]
    assert len(calibrate_satellite_raster_bands(grid, 30.0)) == 1
'''
    },
    "P0097": {
        "domain": "Data Aggregation and Statistics",
        "task": "Aggregate regional healthcare epidemiological risk across layered clinics",
        "category": "All three target issues",
        "code": '''from typing import List, Dict

def audit_regional_health_centers(districts: List[Dict[str, any]], alert_baseline: float) -> List[str]:
    high_risk_centers = []
    for dist in districts:
        for clinic in dist.get("clinics", []):
            composite_risk_index = ((clinic.get("cases", 0) * 12.5) + (clinic.get("positivity_rate", 0.0) * 450.0) - (clinic.get("icu_beds_free", 0) * 8.0)) / (clinic.get("catchment_pop_k", 1.0) * 0.5 + 2.0)
            if ((composite_risk_index > alert_baseline and clinic.get("icu_beds_free", 0) < 3 and dist.get("containment_zone") is not True) or (clinic.get("positivity_rate", 0.0) > 0.25 and clinic.get("cases", 0) > 50 and not clinic.get("emergency_funding", False))) and clinic.get("status") == "ACTIVE":
                high_risk_centers.append(clinic["id"])
    return high_risk_centers

if __name__ == "__main__":
    d = [{"containment_zone": False, "clinics": [{"id": "C10", "cases": 60, "positivity_rate": 0.3, "icu_beds_free": 1, "catchment_pop_k": 20.0, "status": "ACTIVE", "emergency_funding": False}]}]
    assert len(audit_regional_health_centers(d, 50.0)) == 1
'''
    },
    "P0098": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Optimize multi-datacenter server virtual machine placements with thermal caps",
        "category": "All three target issues",
        "code": '''from typing import List, Dict, Tuple

def place_virtual_machines_across_racks(datacenters: List[Dict[str, any]], vm_requests: List[Dict[str, any]]) -> List[Tuple[str, str]]:
    allocations = []
    for dc in datacenters:
        for rack in dc.get("racks", []):
            for server in rack.get("servers", []):
                for vm in vm_requests:
                    placement_efficiency = ((server.get("avail_cpu", 0) - vm.get("req_cpu", 0)) * 1.5) + ((server.get("avail_ram_gb", 0) - vm.get("req_ram_gb", 0)) * 0.8) - (server.get("ambient_temp_c", 20.0) * 0.45)
                    if (not vm.get("assigned") and server.get("avail_cpu", 0) >= vm.get("req_cpu", 0) and server.get("avail_ram_gb", 0) >= vm.get("req_ram_gb", 0) and (dc.get("region") == vm.get("target_region") or vm.get("allow_failover") is True)) and not server.get("maintenance", False):
                        allocations.append((server["id"], vm["id"]))
                        vm["assigned"] = True
    return allocations

if __name__ == "__main__":
    dcs = [{"region": "us-east", "racks": [{"servers": [{"id": "S1", "avail_cpu": 32, "avail_ram_gb": 128, "ambient_temp_c": 22.0, "maintenance": False}]}]}]
    vms = [{"id": "VM1", "req_cpu": 8, "req_ram_gb": 32, "target_region": "us-east", "allow_failover": False, "assigned": False}]
    assert len(place_virtual_machines_across_racks(dcs, vms)) == 1
'''
    },
    "P0099": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Simulate industrial multi-chamber chemical pipeline flow and pressure alarms",
        "category": "All three target issues",
        "code": '''from typing import List, Dict

def simulate_chemical_cascade_pressures(reactors: List[List[Dict[str, any]]], emergency_nitrogen_purge: bool) -> List[Dict[str, any]]:
    critical_events = []
    for row_idx, cascade in enumerate(reactors):
        for col_idx, chamber in enumerate(cascade):
            for vessel in chamber.get("vessels", []):
                membrane_delta_p = ((vessel["inlet_pressure_bar"] - vessel["outlet_pressure_bar"]) * vessel["flow_rate_lpm"] * 0.18) + (vessel["temp_kelvin"] * 0.0035 * vessel.get("viscosity_cp", 1.0)) - 1.25
                if ((membrane_delta_p > 8.5 and vessel.get("valve_state") == "OPEN" and not emergency_nitrogen_purge) or (vessel.get("temp_kelvin", 300) > 450.0 and vessel.get("acid_concentration", 0.0) > 0.65 and not chamber.get("cooling_jacket_active", False))) and not vessel.get("bypassed", False):
                    critical_events.append({"loc": (row_idx, col_idx), "vessel_id": vessel["id"], "delta_p": membrane_delta_p})
    return critical_events

if __name__ == "__main__":
    chem = [[{"cooling_jacket_active": False, "vessels": [{"id": "V1", "inlet_pressure_bar": 12.0, "outlet_pressure_bar": 2.0, "flow_rate_lpm": 10.0, "temp_kelvin": 320.0, "valve_state": "OPEN", "bypassed": False}]}]]
    assert len(simulate_chemical_cascade_pressures(chem, False)) == 1
'''
    },
    "P0100": {
        "domain": "Inventory and Record Management",
        "task": "Audit multi-tiered automated logistics fulfilment routing and customs compliance",
        "category": "All three target issues",
        "code": '''from typing import List, Dict

def audit_cross_border_consignments(distribution_centers: List[Dict[str, any]], sanctioned_countries: List[str]) -> List[Dict[str, any]]:
    flagged_packages = []
    for dc in distribution_centers:
        for bay in dc.get("loading_bays", []):
            for parcel in bay.get("manifested_parcels", []):
                customs_risk_score = ((parcel.get("declared_val_usd", 0.0) * 0.045) + (parcel.get("weight_kg", 0.0) * 3.2) + (parcel.get("prior_flags", 0) * 25.0)) / (parcel.get("shipper_reputation_score", 1.0) + 0.1)
                if ((customs_risk_score > 75.0 and parcel.get("dest_country") in sanctioned_countries and not parcel.get("export_license_verified", False)) or (parcel.get("declared_val_usd", 0.0) > 10000.0 and parcel.get("is_dual_use_technology") is True and not dc.get("customs_bonded", False))) and parcel.get("cleared") is not True:
                    flagged_packages.append({"tracking_number": parcel["tracking_number"], "risk": customs_risk_score})
    return flagged_packages

if __name__ == "__main__":
    dcs = [{"customs_bonded": False, "loading_bays": [{"manifested_parcels": [{"tracking_number": "TRK999", "declared_val_usd": 15000.0, "weight_kg": 20.0, "prior_flags": 1, "shipper_reputation_score": 0.5, "dest_country": "COUNTRY_X", "export_license_verified": False, "is_dual_use_technology": True, "cleared": False}]}]}]
    assert len(audit_cross_border_consignments(dcs, ["COUNTRY_X"])) == 1
'''
    }
}

def main():
    os.makedirs(PROGRAMS_DIR, exist_ok=True)
    
    # 1. Write new program files
    written_count = 0
    new_manifest_rows = []
    
    for pid, data in sorted(PROGRAMS_DATA.items()):
        filename = f"{pid}.py"
        filepath = os.path.join(PROGRAMS_DIR, filename)
        code = data["code"].lstrip()
        
        # Verify AST parsing
        ast.parse(code)
        
        # Write file
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(code)
        written_count += 1
        
        new_manifest_rows.append([
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
        
    print(f"Generated and wrote {written_count} program files (P0051-P0100).")
    
    # 2. Append new rows to manifest.csv
    with open(MANIFEST_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(new_manifest_rows)
        
    print(f"Manifest successfully updated at: {MANIFEST_PATH}")

if __name__ == "__main__":
    main()