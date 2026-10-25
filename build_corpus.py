"""
build_corpus.py
Writes the Batch 7 (P0301-P0350) programs into program_corpus/programs and
appends their rows to program_corpus/manifest.csv. Earlier batches are already
in the corpus and are not rebuilt by this script.

Reruns are safe: identical existing files and manifest rows are skipped, and
any conflicting file or metadata stops the run before anything is written.
New programs must not repeat an existing program (see check_uniqueness).
"""

import ast
import csv
import difflib
import hashlib
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent / "program_corpus"
PROGRAMS_DIR = BASE_DIR / "programs"
MANIFEST_PATH = BASE_DIR / "manifest.csv"

MANIFEST_COLUMNS = [
    "program_id",
    "filename",
    "domain",
    "task_description",
    "intended_category",
    "model_name",
    "prompt_version",
    "generation_batch",
    "syntax_valid",
    "review_status",
]

# New programs whose AST node-type sequence is at least this similar to any
# other program are rejected as near-duplicates. Existing renamed copies in
# the corpus (for example P0131/P0231) score 0.89-0.995.
STRUCTURAL_SIMILARITY_LIMIT = 0.85

BATCH7_PROGRAMS = {
    # 1. NONE (8 programs: P0301 - P0308)
    "P0301": {
        "domain": "Numerical Computation",
        "task": "Integer square root via binary interval halving",
        "category": "None",
        "code": '''def integer_sqrt(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 2:
        return n
    low = 1
    high = n // 2
    best = 1
    while low <= high:
        mid = (low + high) // 2
        square = mid * mid
        if square == n:
            return mid
        if square < n:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    return best

if __name__ == "__main__":
    assert integer_sqrt(0) == 0
    assert integer_sqrt(27) == 5
    assert integer_sqrt(144) == 12
'''
    },
    "P0302": {
        "domain": "String Processing & Text Analysis",
        "task": "Rotational Caesar-13 cipher on ASCII letters preserving case",
        "category": "None",
        "code": '''def rot13_transform(text: str) -> str:
    out = []
    for ch in text:
        code = ord(ch)
        if 65 <= code <= 90:
            out.append(chr(65 + (code - 65 + 13) % 26))
        elif 97 <= code <= 122:
            out.append(chr(97 + (code - 97 + 13) % 26))
        else:
            out.append(ch)
    return "".join(out)

if __name__ == "__main__":
    assert rot13_transform("Hello, World!") == "Uryyb, Jbeyq!"
    assert rot13_transform("Uryyb, Jbeyq!") == "Hello, World!"
'''
    },
    "P0303": {
        "domain": "Searching and Sorting",
        "task": "Lower-bound index of the first element at least target in sorted list",
        "category": "None",
        "code": '''def lower_bound_index(items: list[int], target: int) -> int:
    left = 0
    right = len(items)
    while left < right:
        mid = (left + right) // 2
        if items[mid] < target:
            left = mid + 1
        else:
            right = mid
    return left

if __name__ == "__main__":
    assert lower_bound_index([1, 2, 4, 4, 7], 4) == 2
    assert lower_bound_index([1, 2, 4, 4, 7], 5) == 4
    assert lower_bound_index([1, 2, 4], 9) == 3
'''
    },
    "P0304": {
        "domain": "Data Aggregation and Statistics",
        "task": "Symmetric trimmed mean after dropping outer tail observations",
        "category": "None",
        "code": '''def trimmed_mean(values: list[float], trim_fraction: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    n = len(values)
    cut = int(n * trim_fraction)
    if 2 * cut >= n:
        raise ValueError("trim_fraction removes all observations")
    ordered = sorted(values)
    core = ordered[cut:n - cut]
    return round(sum(core) / len(core), 4)

if __name__ == "__main__":
    assert trimmed_mean([1.0, 2.0, 3.0, 4.0, 100.0], 0.2) == 3.0
    assert trimmed_mean([10.0, 20.0, 30.0], 0.0) == 20.0
'''
    },
    "P0305": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Invert a one-to-one mapping while rejecting duplicate values",
        "category": "None",
        "code": '''def invert_unique_mapping(mapping: dict[str, int]) -> dict[int, str]:
    inverted: dict[int, str] = {}
    for key, value in mapping.items():
        if value in inverted:
            raise ValueError("duplicate value in mapping")
        inverted[value] = key
    return inverted

if __name__ == "__main__":
    assert invert_unique_mapping({"a": 1, "b": 2}) == {1: "a", 2: "b"}
    assert invert_unique_mapping({}) == {}
'''
    },
    "P0306": {
        "domain": "Graph or Tree Traversal",
        "task": "Trace ancestor chain from a node to the root in a parent map",
        "category": "None",
        "code": '''def trace_root_ancestors(parents: dict[str, str], node: str) -> list[str]:
    chain = []
    seen = set()
    current = node
    while current is not None:
        if current in seen:
            raise ValueError("cycle detected in parent links")
        seen.add(current)
        chain.append(current)
        current = parents.get(current)
    return chain

if __name__ == "__main__":
    assert trace_root_ancestors({"d": "b", "b": "a"}, "d") == ["d", "b", "a"]
    assert trace_root_ancestors({}, "root") == ["root"]
'''
    },
    "P0307": {
        "domain": "Inventory and Record Management",
        "task": "Verify double-entry ledger balance across debit and credit postings",
        "category": "None",
        "code": '''def ledger_trial_balance(entries: list[tuple[str, str, int]]) -> tuple[bool, int]:
    debit_cents = 0
    credit_cents = 0
    for account, side, amount in entries:
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if side == "DR":
            debit_cents += amount
        elif side == "CR":
            credit_cents += amount
        else:
            raise ValueError("unknown entry side")
    imbalance = debit_cents - credit_cents
    return imbalance == 0, imbalance

if __name__ == "__main__":
    assert ledger_trial_balance([("cash", "DR", 500), ("sales", "CR", 500)]) == (True, 0)
    assert ledger_trial_balance([("cash", "DR", 500), ("sales", "CR", 450)]) == (False, 50)
'''
    },
    "P0308": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Shortest-processing-time single machine mean flow time",
        "category": "None",
        "code": '''def spt_mean_flow_time(durations: list[float]) -> float:
    if not durations:
        return 0.0
    ordered = sorted(durations)
    elapsed = 0.0
    total_flow = 0.0
    for duration in ordered:
        if duration < 0.0:
            raise ValueError("duration must be non-negative")
        elapsed += duration
        total_flow += elapsed
    return round(total_flow / len(ordered), 4)

if __name__ == "__main__":
    assert spt_mean_flow_time([5.0, 2.0, 8.0]) == 8.0
    assert spt_mean_flow_time([]) == 0.0
'''
    },

    # 2. LONG STATEMENT ONLY (6 programs: P0309 - P0314)
    "P0309": {
        "domain": "Numerical Computation",
        "task": "Tetens saturation vapor pressure and dew point temperature",
        "category": "Long statement only",
        "code": '''import math

def saturation_and_dew_point(temp_c: float, rel_humidity_pct: float) -> tuple[float, float]:
    sat_kpa = 0.61078 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    actual_kpa = sat_kpa * (rel_humidity_pct / 100.0)
    gamma = math.log(actual_kpa / 0.61078)
    dew_point_c = (237.3 * gamma) / (17.27 - gamma)
    return round(sat_kpa, 4), round(dew_point_c, 2)

if __name__ == "__main__":
    sat, dew = saturation_and_dew_point(25.0, 50.0)
    assert abs(sat - 3.1678) < 0.01 and abs(dew - 13.86) < 0.1
'''
    },
    "P0310": {
        "domain": "Data Aggregation and Statistics",
        "task": "Sample excess kurtosis with finite-sample bias adjustment",
        "category": "Long statement only",
        "code": '''def sample_excess_kurtosis(values: list[float]) -> float:
    n = len(values)
    if n < 4:
        raise ValueError("need at least four observations")
    mean = sum(values) / n
    m2 = sum((x - mean) ** 2 for x in values) / n
    m4 = sum((x - mean) ** 4 for x in values) / n
    excess = ((n - 1) / ((n - 2) * (n - 3))) * ((n + 1) * (m4 / (m2 ** 2)) - 3.0 * (n - 1))
    return round(excess, 4)

if __name__ == "__main__":
    assert sample_excess_kurtosis([1.0, 2.0, 3.0, 4.0, 5.0]) == -1.2
'''
    },
    "P0311": {
        "domain": "String Processing & Text Analysis",
        "task": "BM25 single-term relevance score for a document in a collection",
        "category": "Long statement only",
        "code": '''import math

def bm25_term_score(term_freq: int, doc_len: int, avg_doc_len: float, total_docs: int, docs_with_term: int) -> float:
    k1 = 1.5
    b = 0.75
    idf = math.log(1.0 + (total_docs - docs_with_term + 0.5) / (docs_with_term + 0.5))
    tf_norm = (term_freq * (k1 + 1.0)) / (term_freq + k1 * (1.0 - b + b * (doc_len / avg_doc_len)))
    return round(idf * tf_norm, 4)

if __name__ == "__main__":
    assert bm25_term_score(3, 120, 100.0, 1000, 50) > 4.0
    assert bm25_term_score(0, 120, 100.0, 1000, 50) == 0.0
'''
    },
    "P0312": {
        "domain": "Inventory and Record Management",
        "task": "Newsvendor critical fractile and normal optimal order quantity",
        "category": "Long statement only",
        "code": '''import math

def newsvendor_order_quantity(mean_demand: float, demand_sd: float, retail_price: float, unit_cost: float, salvage_value: float) -> tuple[float, float]:
    underage_cost = retail_price - unit_cost
    overage_cost = unit_cost - salvage_value
    critical_fractile = underage_cost / (underage_cost + overage_cost)
    approx_z = 4.91 * (critical_fractile ** 0.14 - (1.0 - critical_fractile) ** 0.14)
    optimal_units = max(0.0, mean_demand + approx_z * demand_sd + 0.0 * math.pi)
    return round(critical_fractile, 4), round(optimal_units, 2)

if __name__ == "__main__":
    frac, qty = newsvendor_order_quantity(200.0, 30.0, 50.0, 20.0, 5.0)
    assert frac == 0.6667 and 212.0 < qty < 214.0
'''
    },
    "P0313": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Single-node RC thermal step response under constant joule heating",
        "category": "Long statement only",
        "code": '''import math

def rc_thermal_step(ambient_c: float, initial_c: float, power_w: float, thermal_res_cw: float, thermal_cap_jc: float, elapsed_s: float) -> float:
    tau = thermal_res_cw * thermal_cap_jc
    steady_state_c = ambient_c + power_w * thermal_res_cw
    instantaneous_c = steady_state_c + (initial_c - steady_state_c) * math.exp(-elapsed_s / tau)
    return round(instantaneous_c, 3)

if __name__ == "__main__":
    assert rc_thermal_step(25.0, 25.0, 10.0, 2.0, 5.0, 0.0) == 25.0
    assert rc_thermal_step(25.0, 25.0, 10.0, 2.0, 5.0, 1000.0) == 45.0
'''
    },
    "P0314": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Kingman VUT queue waiting time approximation for a single workstation",
        "category": "Long statement only",
        "code": '''def kingman_wait_minutes(arrival_rate_per_hr: float, service_rate_per_hr: float, cv_arrival: float, cv_service: float) -> float:
    utilization = arrival_rate_per_hr / service_rate_per_hr
    if utilization >= 1.0 or utilization <= 0.0:
        raise ValueError("utilization must be strictly between 0 and 1")
    mean_service_min = 60.0 / service_rate_per_hr
    expected_wait_min = ((cv_arrival ** 2 + cv_service ** 2) / 2.0) * (utilization / (1.0 - utilization)) * mean_service_min
    return round(expected_wait_min, 3)

if __name__ == "__main__":
    assert kingman_wait_minutes(12.0, 15.0, 1.0, 1.0) == 16.0
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0315 - P0320)
    "P0315": {
        "domain": "Searching and Sorting",
        "task": "Odd-even transposition brick sort for a list of integers",
        "category": "Nested loop only",
        "code": '''def odd_even_brick_sort(values: list[int]) -> list[int]:
    arr = list(values)
    n = len(arr)
    for phase in range(n):
        start = phase % 2
        for idx in range(start, n - 1, 2):
            if arr[idx] > arr[idx + 1]:
                arr[idx], arr[idx + 1] = arr[idx + 1], arr[idx]
    return arr

if __name__ == "__main__":
    assert odd_even_brick_sort([9, 3, 7, 1, 5, 2]) == [1, 2, 3, 5, 7, 9]
    assert odd_even_brick_sort([]) == []
'''
    },
    "P0316": {
        "domain": "Matrix & Grid Operations",
        "task": "Lower-triangular Pascal binomial table up to order n",
        "category": "Nested loop only",
        "code": '''def pascal_triangle_table(order: int) -> list[list[int]]:
    rows = []
    for r in range(order + 1):
        row = [1] * (r + 1)
        for c in range(1, r):
            row[c] = rows[r - 1][c - 1] + rows[r - 1][c]
        rows.append(row)
    return rows

if __name__ == "__main__":
    assert pascal_triangle_table(4)[-1] == [1, 4, 6, 4, 1]
    assert pascal_triangle_table(0) == [[1]]
'''
    },
    "P0317": {
        "domain": "String Processing & Text Analysis",
        "task": "Character transition bigram count matrix across a word list",
        "category": "Nested loop only",
        "code": '''def character_bigram_counts(words: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for word in words:
        cleaned = word.lower()
        for idx in range(len(cleaned) - 1):
            pair = cleaned[idx:idx + 2]
            counts[pair] = counts.get(pair, 0) + 1
    return counts

if __name__ == "__main__":
    assert character_bigram_counts(["banana"]) == {"ba": 1, "an": 2, "na": 2}
    assert character_bigram_counts(["a", ""]) == {}
'''
    },
    "P0318": {
        "domain": "Graph or Tree Traversal",
        "task": "Kahn topological ordering of a directed acyclic graph",
        "category": "Nested loop only",
        "code": '''from collections import deque

def kahn_topological_order(graph: dict[str, list[str]]) -> list[str]:
    in_degree = {u: 0 for u in graph}
    for u, neighbors in graph.items():
        for v in neighbors:
            in_degree[v] = in_degree.get(v, 0) + 1
    zero_nodes = [u for u, d in in_degree.items() if d == 0]
    ready = deque(sorted(zero_nodes))
    order = []
    while ready:
        node = ready.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            in_degree[nxt] -= 1
            if in_degree[nxt] == 0:
                ready.append(nxt)
    return order

if __name__ == "__main__":
    g = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}
    assert kahn_topological_order(g) == ["a", "b", "c", "d"]
'''
    },
    "P0319": {
        "domain": "Data Aggregation and Statistics",
        "task": "Empirical joint histogram over two-dimensional bin edges",
        "category": "Nested loop only",
        "code": '''def joint_grid_histogram(xs: list[float], ys: list[float], bins: int) -> list[list[int]]:
    grid = []
    for _ in range(bins):
        grid.append([0] * bins)
    for r in range(bins):
        for c in range(bins):
            for x, y in zip(xs, ys):
                ix = min(bins - 1, max(0, int(x * bins)))
                iy = min(bins - 1, max(0, int(y * bins)))
                if ix == r and iy == c:
                    grid[r][c] += 1
    return grid

if __name__ == "__main__":
    xs, ys = [0.1, 0.1, 0.9], [0.2, 0.8, 0.9]
    assert joint_grid_histogram(xs, ys, 2) == [[1, 1], [0, 1]]
'''
    },
    "P0320": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Abelian sandpile toppling relaxation on a square grid",
        "category": "Nested loop only",
        "code": '''def relax_abelian_sandpile(initial: list[list[int]]) -> list[list[int]]:
    size = len(initial)
    grid = [row[:] for row in initial]
    changed = True
    while changed:
        changed = False
        for r in range(size):
            for c in range(size):
                if grid[r][c] >= 4:
                    spill = grid[r][c] // 4
                    grid[r][c] %= 4
                    changed = True
                    if r > 0:
                        grid[r - 1][c] += spill
                    if r + 1 < size:
                        grid[r + 1][c] += spill
                    if c > 0:
                        grid[r][c - 1] += spill
                    if c + 1 < size:
                        grid[r][c + 1] += spill
    return grid

if __name__ == "__main__":
    assert relax_abelian_sandpile([[0, 0, 0], [0, 4, 0], [0, 0, 0]]) == [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
'''
    },

    # 4. COMPLEX CONDITIONAL ONLY (6 programs: P0321 - P0326)
    "P0321": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate semantic version strings with optional pre-release tags",
        "category": "Complex conditional only",
        "code": '''def is_valid_semver(version: str) -> bool:
    core, sep, prerelease = version.partition("-")
    parts = core.split(".")
    if len(parts) != 3 or (sep == "-" and not prerelease):
        return False
    for num in parts:
        if not num.isdigit() or (len(num) > 1 and num.startswith("0")):
            return False
    if prerelease:
        for ident in prerelease.split("."):
            if not ident or not ident.replace("-", "").isalnum():
                return False
            if ident.isdigit() and len(ident) > 1 and ident.startswith("0"):
                return False
    return True

if __name__ == "__main__":
    assert is_valid_semver("1.2.3-alpha.1") is True
    assert is_valid_semver("01.2.3") is False
    assert is_valid_semver("1.2.3-01") is False
'''
    },
    "P0322": {
        "domain": "Numerical Computation",
        "task": "Check strict diagonal dominance and positivity of a 3x3 matrix",
        "category": "Complex conditional only",
        "code": '''def is_strictly_diagonally_dominant_3x3(m: list[list[float]]) -> bool:
    if len(m) != 3 or len(m[0]) != 3 or len(m[1]) != 3 or len(m[2]) != 3:
        return False
    d0, d1, d2 = abs(m[0][0]), abs(m[1][1]), abs(m[2][2])
    r0 = abs(m[0][1]) + abs(m[0][2])
    r1 = abs(m[1][0]) + abs(m[1][2])
    r2 = abs(m[2][0]) + abs(m[2][1])
    if d0 <= r0 or d1 <= r1 or d2 <= r2:
        return False
    return m[0][0] > 0 and m[1][1] > 0 and m[2][2] > 0

if __name__ == "__main__":
    assert is_strictly_diagonally_dominant_3x3([[4, -1, 1], [1, 5, -2], [0, 2, 3]]) is True
    assert is_strictly_diagonally_dominant_3x3([[2, -1, 1], [1, 5, -2], [0, 2, 3]]) is False
'''
    },
    "P0323": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Determine blood donor deferral status from vitals and recent history",
        "category": "Complex conditional only",
        "code": '''def is_blood_donor_eligible(age: int, weight_kg: float, hemoglobin_g_dl: float, days_since_donation: int, recent_tattoo: bool) -> bool:
    if age < 18 or age > 65 or weight_kg < 50.0:
        return False
    if hemoglobin_g_dl < 12.5 or hemoglobin_g_dl > 18.5:
        return False
    if days_since_donation < 56 or recent_tattoo:
        return False
    return True

if __name__ == "__main__":
    assert is_blood_donor_eligible(30, 65.0, 14.2, 90, False) is True
    assert is_blood_donor_eligible(30, 65.0, 11.8, 90, False) is False
    assert is_blood_donor_eligible(30, 65.0, 14.2, 40, False) is False
'''
    },
    "P0324": {
        "domain": "Inventory and Record Management",
        "task": "Determine whether a warehouse bin can accept an incoming cold-storage lot",
        "category": "Complex conditional only",
        "code": '''def can_store_lot_in_bin(free_slots: int, pallets: int, cold_lot: bool, cold_bin: bool, temp_c: float, locked: bool) -> bool:
    if locked or pallets <= 0 or free_slots < pallets:
        return False
    if cold_lot and (not cold_bin or temp_c > 4.0):
        return False
    return True

if __name__ == "__main__":
    assert can_store_lot_in_bin(6, 3, True, True, 2.5, False) is True
    assert can_store_lot_in_bin(6, 3, True, True, 8.0, False) is False
    assert can_store_lot_in_bin(2, 5, False, False, 20.0, False) is False
'''
    },
    "P0325": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Select elevator cabin dispatch state from hall calls, load and fire mode",
        "category": "Complex conditional only",
        "code": '''def elevator_dispatch_action(floor: int, target: int, load_kg: float, max_kg: float, fire_alarm: bool, door_blocked: bool) -> str:
    if fire_alarm and floor != 1 and not door_blocked:
        return "RECALL_GROUND"
    if door_blocked or load_kg > max_kg:
        return "HOLD_ALARM"
    if fire_alarm and floor == 1:
        return "PARK_OPEN"
    if target > floor and load_kg <= max_kg:
        return "ASCEND"
    if target < floor and load_kg <= max_kg:
        return "DESCEND"
    return "IDLE"

if __name__ == "__main__":
    assert elevator_dispatch_action(5, 8, 300.0, 800.0, True, False) == "RECALL_GROUND"
    assert elevator_dispatch_action(3, 7, 900.0, 800.0, False, False) == "HOLD_ALARM"
    assert elevator_dispatch_action(2, 6, 400.0, 800.0, False, False) == "ASCEND"
'''
    },
    "P0326": {
        "domain": "Matrix & Grid Operations",
        "task": "Check legality of a rook slide along an unobstructed rank or file",
        "category": "Complex conditional only",
        "code": '''def is_legal_rook_slide(start: tuple[int, int], end: tuple[int, int], occupied: set[tuple[int, int]]) -> bool:
    r1, c1 = start
    r2, c2 = end
    if start == end or (r1 != r2 and c1 != c2) or not (0 <= r2 < 8 and 0 <= c2 < 8):
        return False
    dr = 0 if r1 == r2 else (1 if r2 > r1 else -1)
    dc = 0 if c1 == c2 else (1 if c2 > c1 else -1)
    cr, cc = r1 + dr, c1 + dc
    while (cr, cc) != (r2, c2):
        if (cr, cc) in occupied:
            return False
        cr += dr
        cc += dc
    return end not in occupied

if __name__ == "__main__":
    assert is_legal_rook_slide((0, 0), (0, 5), {(0, 7)}) is True
    assert is_legal_rook_slide((0, 0), (0, 5), {(0, 3)}) is False
    assert is_legal_rook_slide((1, 1), (3, 4), set()) is False
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (6 programs: P0327 - P0332)
    "P0327": {
        "domain": "Numerical Computation",
        "task": "Gauss-Seidel iterative solver for a square linear system",
        "category": "Long statement and nested loop",
        "code": '''def gauss_seidel_solve(a: list[list[float]], b: list[float], iterations: int) -> list[float]:
    n = len(b)
    x = [0.0] * n
    for _ in range(iterations):
        for i in range(n):
            off_diag = sum(a[i][j] * x[j] for j in range(n) if j != i)
            x[i] = (b[i] - off_diag) / a[i][i]
    return [round(val, 5) for val in x]

if __name__ == "__main__":
    sol = gauss_seidel_solve([[4.0, 1.0], [2.0, 3.0]], [1.0, 2.0], 25)
    assert sol == [0.1, 0.6]
'''
    },
    "P0328": {
        "domain": "Data Aggregation and Statistics",
        "task": "Bhattacharyya distance between normalized two-dimensional histograms",
        "category": "Long statement and nested loop",
        "code": '''import math

def bhattacharyya_grid_distance(hist_p: list[list[float]], hist_q: list[list[float]]) -> float:
    total_p = sum(sum(row) for row in hist_p)
    total_q = sum(sum(row) for row in hist_q)
    coeff = 0.0
    for r in range(len(hist_p)):
        for c in range(len(hist_p[r])):
            coeff += math.sqrt((hist_p[r][c] / total_p) * (hist_q[r][c] / total_q))
    return round(-math.log(max(1e-12, min(1.0, coeff))), 5)

if __name__ == "__main__":
    assert bhattacharyya_grid_distance([[1.0, 2.0], [3.0, 4.0]], [[1.0, 2.0], [3.0, 4.0]]) == 0.0
    assert bhattacharyya_grid_distance([[9.0, 1.0], [1.0, 1.0]], [[1.0, 1.0], [1.0, 9.0]]) > 0.3
'''
    },
    "P0329": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Coupled Kuramoto phase oscillators synchronization step",
        "category": "Long statement and nested loop",
        "code": '''import math

def kuramoto_step(phases: list[float], natural_freqs: list[float], coupling: float, dt: float) -> list[float]:
    n = len(phases)
    updated = []
    for i in range(n):
        interaction = 0.0
        for j in range(n):
            interaction += math.sin(phases[j] - phases[i])
        next_phase = phases[i] + dt * (natural_freqs[i] + (coupling / n) * interaction)
        updated.append(round(next_phase, 6))
    return updated

if __name__ == "__main__":
    res = kuramoto_step([0.0, 1.0], [0.5, 0.5], 2.0, 0.1)
    assert res[0] > 0.05 and res[1] < 1.05
'''
    },
    "P0330": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Proportional-fair downlink wireless resource block throughput matrix",
        "category": "Long statement and nested loop",
        "code": '''import math

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
'''
    },
    "P0331": {
        "domain": "Inventory and Record Management",
        "task": "Multi-period Wagner-Whitin dynamic lot-sizing cost table",
        "category": "Long statement and nested loop",
        "code": '''def wagner_whitin_min_cost(demands: list[int], setup_cost: float, holding_cost: float) -> float:
    periods = len(demands)
    dp = [float("inf")] * (periods + 1)
    dp[0] = 0.0
    for t in range(1, periods + 1):
        for s in range(1, t + 1):
            carry_cost = sum((k - s) * demands[k - 1] * holding_cost for k in range(s, t + 1))
            dp[t] = min(dp[t], dp[s - 1] + setup_cost + carry_cost)
    return round(dp[periods], 2)

if __name__ == "__main__":
    assert wagner_whitin_min_cost([20, 30, 10], 100.0, 2.0) == 200.0
'''
    },
    "P0332": {
        "domain": "Matrix & Grid Operations",
        "task": "Bilateral-weighted smoothing of a one-dimensional signal with spatial and range kernels",
        "category": "Long statement and nested loop",
        "code": '''import math

def bilateral_filter_1d(signal: list[float], sigma_spatial: float, sigma_range: float) -> list[float]:
    n = len(signal)
    smoothed = []
    for i in range(n):
        num = 0.0
        den = 0.0
        for j in range(n):
            weight = math.exp(-((i - j) ** 2) / (2.0 * sigma_spatial ** 2) - ((signal[i] - signal[j]) ** 2) / (2.0 * sigma_range ** 2))
            num += weight * signal[j]
            den += weight
        smoothed.append(round(num / den, 4))
    return smoothed

if __name__ == "__main__":
    out = bilateral_filter_1d([1.0, 1.0, 10.0, 10.0], 1.0, 0.5)
    assert out[0] < 1.1 and out[3] > 9.9
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0333 - P0338)
    "P0333": {
        "domain": "Numerical Computation",
        "task": "Snell acoustic refraction angle and critical total internal reflection check",
        "category": "Long statement and complex conditional",
        "code": '''import math

def snell_refraction_deg(incident_deg: float, c_medium1: float, c_medium2: float) -> tuple[str, float]:
    if incident_deg < 0.0 or incident_deg >= 90.0 or c_medium1 <= 0.0 or c_medium2 <= 0.0:
        raise ValueError("invalid angle or wave speeds")
    sin_transmitted = (c_medium2 / c_medium1) * math.sin(math.radians(incident_deg))
    if sin_transmitted >= 1.0:
        critical_deg = math.degrees(math.asin(c_medium1 / c_medium2))
        return ("total_internal_reflection", round(critical_deg, 3))
    transmitted_deg = math.degrees(math.asin(sin_transmitted))
    return ("refracted", round(transmitted_deg, 3))

if __name__ == "__main__":
    assert snell_refraction_deg(30.0, 1500.0, 1500.0) == ("refracted", 30.0)
    assert snell_refraction_deg(60.0, 1500.0, 3000.0) == ("total_internal_reflection", 30.0)
'''
    },
    "P0334": {
        "domain": "Data Aggregation and Statistics",
        "task": "Two-sample Welch t-statistic and significance decision",
        "category": "Long statement and complex conditional",
        "code": '''import math

def welch_t_decision(mean1: float, var1: float, n1: int, mean2: float, var2: float, n2: int, critical_t: float) -> tuple[float, bool]:
    if n1 < 2 or n2 < 2 or var1 < 0.0 or var2 < 0.0 or (var1 == 0.0 and var2 == 0.0):
        raise ValueError("invalid sample statistics")
    se = math.sqrt(var1 / n1 + var2 / n2)
    t_stat = (mean1 - mean2) / se
    df_num = (var1 / n1 + var2 / n2) ** 2
    df_den = (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
    reject = abs(t_stat) >= critical_t and (df_num / df_den) >= 4.0 and se > 0.0
    return round(t_stat, 4), reject

if __name__ == "__main__":
    assert welch_t_decision(10.0, 4.0, 16, 7.0, 4.0, 16, 2.0) == (4.2426, True)
'''
    },
    "P0335": {
        "domain": "String Processing & Text Analysis",
        "task": "DKIM email header tag parser and cryptographic policy check",
        "category": "Long statement and complex conditional",
        "code": '''def evaluate_dkim_header(header: str, now_epoch: int) -> tuple[bool, int]:
    tags = {}
    for item in header.split(";"):
        key, sep, val = item.strip().partition("=")
        if sep:
            tags[key.strip()] = val.strip()
    algo = tags.get("a", "")
    created = int(tags.get("t", "0"))
    expires = int(tags.get("x", str(now_epoch + 3600)))
    if tags.get("v") != "1" or algo not in ("rsa-sha256", "ed25519-sha256") or not tags.get("b") or not tags.get("d"):
        return False, 0
    if created > now_epoch or expires <= now_epoch or (expires - created) > 7 * 86400:
        return False, 0
    remaining_validity_hours = int((expires - now_epoch) / 3600.0 + (24 if algo == "ed25519-sha256" else 0))
    return True, remaining_validity_hours

if __name__ == "__main__":
    assert evaluate_dkim_header("v=1; a=rsa-sha256; d=example.org; b=xyz; t=1000; x=8200", 1000) == (True, 2)
    assert evaluate_dkim_header("v=1; a=rsa-sha1; d=example.org; b=xyz", 1000) == (False, 0)
'''
    },
    "P0336": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Lithium-ion cell fast-charge current taper and thermal cutback",
        "category": "Long statement and complex conditional",
        "code": '''def fast_charge_current_amps(soc: float, temp_c: float, cell_v: float, capacity_ah: float, fault_flag: bool) -> float:
    if fault_flag or temp_c < 0.0 or temp_c > 55.0 or cell_v >= 4.25 or soc >= 1.0:
        return 0.0
    base_c_rate = 2.0 if 15.0 <= temp_c <= 40.0 and soc < 0.5 else 1.0
    voltage_taper = max(0.1, (4.20 - max(3.60, cell_v)) / 0.60)
    commanded_amps = capacity_ah * base_c_rate * min(1.0, voltage_taper) * (1.0 - 0.5 * max(0.0, soc - 0.8) / 0.2)
    return round(commanded_amps, 3)

if __name__ == "__main__":
    assert fast_charge_current_amps(0.3, 25.0, 3.6, 50.0, False) == 100.0
    assert fast_charge_current_amps(0.3, -5.0, 3.6, 50.0, False) == 0.0
'''
    },
    "P0337": {
        "domain": "Inventory and Record Management",
        "task": "Letter-of-credit documentary discrepancy fee and payment release",
        "category": "Long statement and complex conditional",
        "code": '''def release_letter_of_credit(face_usd: float, shipped_days_late: int, invoice_usd: float, clean_bill: bool, insured: bool, sanctioned: bool) -> tuple[bool, float]:
    if sanctioned or not clean_bill or not insured or shipped_days_late > 5 or invoice_usd > face_usd * 1.05:
        return False, 0.0
    overrun_usd = max(0.0, invoice_usd - face_usd)
    discrepancy_fee = (75.0 if shipped_days_late > 0 else 0.0) + 0.02 * overrun_usd + 0.0015 * invoice_usd
    net_payout = invoice_usd - discrepancy_fee
    return True, round(net_payout, 2)

if __name__ == "__main__":
    assert release_letter_of_credit(10000.0, 0, 10000.0, True, True, False) == (True, 9985.0)
    assert release_letter_of_credit(10000.0, 7, 10000.0, True, True, False) == (False, 0.0)
'''
    },
    "P0338": {
        "domain": "Scheduling and Resource Allocation",
        "task": "EV charging depot transformer load curtailment and session tariff",
        "category": "Long statement and complex conditional",
        "code": '''def ev_depot_session_quote(requested_kwh: float, dwell_hours: float, grid_load_pct: float, peak_window: bool, fleet_contract: bool) -> tuple[float, float]:
    if requested_kwh <= 0.0 or dwell_hours <= 0.0 or grid_load_pct >= 98.0:
        return 0.0, 0.0
    max_charger_kw = 22.0 if grid_load_pct < 80.0 and not (peak_window and not fleet_contract) else 11.0
    delivered_kwh = min(requested_kwh, max_charger_kw * dwell_hours)
    rate_per_kwh = 0.18 + (0.09 if peak_window else 0.0) - (0.04 if fleet_contract else 0.0)
    total_charge = delivered_kwh * rate_per_kwh + (1.50 * dwell_hours if dwell_hours > 8.0 and not fleet_contract else 0.0)
    return round(delivered_kwh, 2), round(total_charge, 2)

if __name__ == "__main__":
    assert ev_depot_session_quote(40.0, 2.0, 60.0, False, True) == (40.0, 5.6)
    assert ev_depot_session_quote(40.0, 2.0, 99.0, False, True) == (0.0, 0.0)
'''
    },

    # 7. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0339 - P0344)
    "P0339": {
        "domain": "Matrix & Grid Operations",
        "task": "Find interior grid cells that are strict local extrema along both axes",
        "category": "Nested loop and complex conditional",
        "code": '''def find_axial_extrema(grid: list[list[float]]) -> list[tuple[int, int, str]]:
    rows, cols = len(grid), len(grid[0])
    extrema = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            val = grid[r][c]
            up, down = grid[r - 1][c], grid[r + 1][c]
            left, right = grid[r][c - 1], grid[r][c + 1]
            if val > up and val > down and val > left and val > right:
                extrema.append((r, c, "peak"))
            elif val < up and val < down and val < left and val < right:
                extrema.append((r, c, "pit"))
    return extrema

if __name__ == "__main__":
    assert find_axial_extrema([[1, 2, 1], [2, 9, 2], [1, 2, 1]]) == [(1, 1, "peak")]
    assert find_axial_extrema([[5, 4, 5], [4, 0, 4], [5, 4, 5]]) == [(1, 1, "pit")]
'''
    },
    "P0340": {
        "domain": "Graph or Tree Traversal",
        "task": "Detect directed two-hop broker bridges between isolated security zones",
        "category": "Nested loop and complex conditional",
        "code": '''def find_zone_broker_bridges(edges: dict[str, list[str]], zones: dict[str, str], cleared: set[str]) -> list[tuple[str, str, str]]:
    bridges = []
    for src, mids in edges.items():
        for mid in mids:
            for dst in edges.get(mid, []):
                if src != dst and zones.get(src) != zones.get(dst) and mid in cleared and dst not in mids:
                    bridges.append((src, mid, dst))
    return sorted(bridges)

if __name__ == "__main__":
    g = {"n1": ["b1"], "b1": ["n2"], "n2": []}
    assert find_zone_broker_bridges(g, {"n1": "red", "b1": "dmz", "n2": "blue"}, {"b1"}) == [("n1", "b1", "n2")]
'''
    },
    "P0341": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Find radio channel co-channel interference conflicts across base stations",
        "category": "Nested loop and complex conditional",
        "code": '''def find_channel_interference_pairs(towers: list[tuple[str, float, float, float, int, bool]]) -> list[tuple[str, str]]:
    conflicts = []
    for i in range(len(towers)):
        for j in range(i + 1, len(towers)):
            id_a, xa, ya, ra, ch_a, on_a = towers[i]
            id_b, xb, yb, rb, ch_b, on_b = towers[j]
            dist_sq = (xa - xb) ** 2 + (ya - yb) ** 2
            limit_sq = (ra + rb) ** 2
            if on_a and on_b and abs(ch_a - ch_b) <= 1 and dist_sq < limit_sq:
                conflicts.append((id_a, id_b))
    return conflicts

if __name__ == "__main__":
    t1 = ("T1", 0.0, 0.0, 5.0, 6, True)
    t2 = ("T2", 3.0, 4.0, 2.0, 6, True)
    assert find_channel_interference_pairs([t1, t2]) == [("T1", "T2")]
'''
    },
    "P0342": {
        "domain": "String Processing & Text Analysis",
        "task": "Match log lines against multi-clause intrusion detection signatures",
        "category": "Nested loop and complex conditional",
        "code": '''def match_intrusion_signatures(logs: list[str], rules: list[tuple[str, str, str, str]]) -> list[tuple[int, str]]:
    hits = []
    for idx, raw in enumerate(logs):
        lower = raw.lower()
        for name, kw1, kw2, allow_tag in rules:
            if kw1 in lower and kw2 in lower and allow_tag not in lower:
                hits.append((idx, name))
    return hits

if __name__ == "__main__":
    rule = ("SQLI", "union", "select", "ok")
    sample = ["GET /q?x=UNION+SELECT", "ok UNION SELECT"]
    assert match_intrusion_signatures(sample, [rule]) == [(0, "SQLI")]
'''
    },
    "P0343": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Advance vehicle platooning gap regulation across highway lanes",
        "category": "Nested loop and complex conditional",
        "code": '''def step_lane_platoons(lanes: list[list[tuple[float, float, bool]]], safe_gap: float) -> list[list[str]]:
    commands = []
    for lane in lanes:
        lane_cmds = ["CRUISE"]
        for idx in range(1, len(lane)):
            lead_pos, lead_v, _ = lane[idx - 1]
            fol_pos, fol_v, manual = lane[idx]
            gap = lead_pos - fol_pos
            if gap < safe_gap and fol_v > lead_v and not manual:
                lane_cmds.append("BRAKE")
            elif gap > safe_gap * 2.0 and fol_v <= lead_v and not manual:
                lane_cmds.append("ACCEL")
            else:
                lane_cmds.append("CRUISE")
        commands.append(lane_cmds)
    return commands

if __name__ == "__main__":
    cars = [(100.0, 20.0, False), (90.0, 25.0, False)]
    assert step_lane_platoons([cars], 15.0) == [["CRUISE", "BRAKE"]]
'''
    },
    "P0344": {
        "domain": "Inventory and Record Management",
        "task": "Cross-match blood bank unit bags to compatible patient requests",
        "category": "Nested loop and complex conditional",
        "code": '''def allocate_blood_units(requests: list[tuple[str, str, int]], bags: list[tuple[str, str, int, int]]) -> dict[str, str]:
    used = set()
    assigned = {}
    for pid, req_abo, min_ml in requests:
        for bid, bag_abo, days_left, vol_ml in bags:
            if bid in used:
                continue
            if (bag_abo == "O" or bag_abo == req_abo) and days_left >= 2 and vol_ml >= min_ml:
                assigned[pid] = bid
                used.add(bid)
                break
    return assigned

if __name__ == "__main__":
    reqs = [("P1", "A", 450)]
    stock = [("B1", "B", 10, 500), ("B2", "O", 5, 500)]
    assert allocate_blood_units(reqs, stock) == {"P1": "B2"}
'''
    },

    # 8. ALL THREE TARGET ISSUES (6 programs: P0345 - P0350)
    "P0345": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Gaussian plume downwind atmospheric pollutant dispersion grid alert",
        "category": "All three target issues",
        "code": '''import math

def dispersion_grid_exceedances(sources: list[dict[str, float]], receptors: list[tuple[float, float]], wind_ms: float, limit_ug_m3: float) -> list[tuple[int, float]]:
    exceeded = []
    for idx, (rx, ry) in enumerate(receptors):
        total_conc = 0.0
        for src in sources:
            dx = rx - src["x"]
            dy = ry - src["y"]
            if dx > 0.0 and wind_ms >= 0.5 and src["emission_g_s"] > 0.0:
                sigma_y = 0.08 * dx * (1.0 + 0.0001 * dx) ** (-0.5)
                sigma_z = 0.06 * dx * (1.0 + 0.0015 * dx) ** (-0.5)
                plume_ug_m3 = (src["emission_g_s"] * 1e6 / (math.pi * wind_ms * sigma_y * sigma_z)) * math.exp(-0.5 * (dy / sigma_y) ** 2 - 0.5 * (src["stack_m"] / sigma_z) ** 2)
                total_conc += plume_ug_m3
        if total_conc >= limit_ug_m3:
            exceeded.append((idx, round(total_conc, 2)))
    return exceeded

if __name__ == "__main__":
    hits = dispersion_grid_exceedances([{"x": 0.0, "y": 0.0, "stack_m": 10.0, "emission_g_s": 50.0}], [(500.0, 0.0), (-100.0, 0.0)], 4.0, 100.0)
    assert len(hits) == 1 and hits[0][0] == 0
'''
    },
    "P0346": {
        "domain": "Matrix & Grid Operations",
        "task": "Synthetic aperture radar phase interferogram coherence and fringe detector",
        "category": "All three target issues",
        "code": '''import math

def detect_insar_fringe_cells(amp: list[list[float]], phase: list[list[float]], min_amp: float) -> list[tuple[int, int, float]]:
    rows, cols = len(amp), len(amp[0])
    fringes = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            grad_x = math.atan2(math.sin(phase[r][c + 1] - phase[r][c - 1]), math.cos(phase[r][c + 1] - phase[r][c - 1]))
            grad_y = math.atan2(math.sin(phase[r + 1][c] - phase[r - 1][c]), math.cos(phase[r + 1][c] - phase[r - 1][c]))
            fringe_rate = math.hypot(grad_x, grad_y)
            if amp[r][c] >= min_amp and amp[r][c + 1] >= min_amp and fringe_rate > 1.2:
                fringes.append((r, c, round(fringe_rate, 3)))
    return fringes

if __name__ == "__main__":
    a = [[5.0, 5.0, 5.0], [5.0, 5.0, 5.0], [5.0, 5.0, 5.0]]
    p = [[0.0, 0.0, 0.0], [0.0, 1.0, 2.5], [0.0, 0.0, 0.0]]
    assert detect_insar_fringe_cells(a, p, 2.0) == [(1, 1, 2.5)]
'''
    },
    "P0347": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Assign maritime harbour tugboats to incoming vessels under bollard pull and draft rules",
        "category": "All three target issues",
        "code": '''def assign_harbour_tugboats(vessels: list[dict], tugs: list[dict], tide_m: float) -> dict[str, str]:
    busy = set()
    berth_plan = {}
    for vessel in sorted(vessels, key=lambda v: -v["tonnage"]):
        required_pull_t = 0.0012 * vessel["tonnage"] + 0.8 * vessel["wind_area_m2"] * (vessel["wind_kts"] / 20.0) ** 2
        for tug in tugs:
            if tug["id"] in busy:
                continue
            if tug["bollard_pull_t"] >= required_pull_t and vessel["draft_m"] <= tug["channel_depth_m"] + tide_m and (not vessel["hazmat"] or tug["firefighting"]):
                berth_plan[vessel["imo"]] = tug["id"]
                busy.add(tug["id"])
                break
    return berth_plan

if __name__ == "__main__":
    v = [{"imo": "V1", "tonnage": 30000, "wind_area_m2": 500.0, "wind_kts": 10.0, "draft_m": 11.0, "hazmat": True}]
    t = [{"id": "T1", "bollard_pull_t": 150.0, "channel_depth_m": 10.0, "firefighting": True}]
    assert assign_harbour_tugboats(v, t, 2.0) == {"V1": "T1"}
'''
    },
    "P0348": {
        "domain": "Inventory and Record Management",
        "task": "Reconcile fuel depot tank strapping dip readings against metered flow totals",
        "category": "All three target issues",
        "code": '''def audit_depot_tank_losses(depots: list[dict], max_loss_pct: float) -> list[tuple[str, str, float]]:
    alerts = []
    for depot in depots:
        for tank in depot["tanks"]:
            thermal_factor = 1.0 - 0.00085 * (tank["temp_c"] - 15.0)
            expected_liters = (tank["opening_l"] + sum(tank["receipts_l"]) - sum(tank["dispensed_l"])) * thermal_factor
            variance_pct = abs(tank["strapped_l"] - expected_liters) / max(1.0, expected_liters) * 100.0
            if variance_pct > max_loss_pct and tank["water_bottom_mm"] < 25.0 and not tank.get("meter_calibrating", False):
                alerts.append((depot["code"], tank["id"], round(variance_pct, 2)))
    return alerts

if __name__ == "__main__":
    tank = {"id": "TK1", "temp_c": 15.0, "opening_l": 10000.0, "receipts_l": [2000.0], "dispensed_l": [1000.0], "strapped_l": 10500.0, "water_bottom_mm": 5.0}
    assert audit_depot_tank_losses([{"code": "D1", "tanks": [tank]}], 2.0) == [("D1", "TK1", 4.55)]
'''
    },
    "P0349": {
        "domain": "Numerical Computation",
        "task": "Grid search of Tuned Mass Damper parameters for structural resonance suppression",
        "category": "All three target issues",
        "code": '''import math

def optimize_tuned_mass_damper(freq_ratios: list[float], damping_ratios: list[float], mass_ratio: float) -> tuple[float, float, float]:
    best = (0.0, 0.0, float("inf"))
    for f_ratio in freq_ratios:
        for zeta in damping_ratios:
            if f_ratio <= 0.5 or zeta <= 0.01 or zeta >= 0.5:
                continue
            peak_amp = 0.0
            for step in range(80, 121):
                g = step / 100.0
                real_part = (f_ratio ** 2 - g ** 2) * (1.0 - g ** 2) - mass_ratio * (g ** 2) * (f_ratio ** 2)
                imag_part = 2.0 * zeta * g * f_ratio * (1.0 - g ** 2 * (1.0 + mass_ratio))
                amp = math.hypot(f_ratio ** 2 - g ** 2, 2.0 * zeta * g * f_ratio) / max(1e-9, math.hypot(real_part, imag_part))
                peak_amp = max(peak_amp, amp)
            if peak_amp < best[2]:
                best = (f_ratio, zeta, round(peak_amp, 3))
    return best

if __name__ == "__main__":
    res = optimize_tuned_mass_damper([0.95, 1.0], [0.05, 0.12], 0.05)
    assert res[0] == 0.95 and res[2] < 10.0
'''
    },
    "P0350": {
        "domain": "Data Aggregation and Statistics",
        "task": "Flag clinical lab panels with multivariate z-score drift and hemolysis interference",
        "category": "All three target issues",
        "code": '''def flag_anomalous_lab_panels(panels: list[dict], ref_bounds: dict[str, tuple[float, float]]) -> list[str]:
    flagged = []
    for panel in panels:
        extreme_count = 0
        mahalanobis_sq = 0.0
        for analyte, value in panel["analytes"].items():
            mean, sd = ref_bounds[analyte]
            z_score = (value - mean) / max(1e-6, sd)
            mahalanobis_sq += z_score * z_score
            if abs(z_score) >= 2.5 and not panel["fasting_exempt"] and analyte != "glucose":
                extreme_count += 1
        composite_index = mahalanobis_sq / max(1, len(panel["analytes"])) + 1.5 * extreme_count - (0.8 if panel["hemolysis_index"] > 50.0 else 0.0)
        if composite_index >= 4.0 and panel["hemolysis_index"] <= 100.0 and not panel.get("retest_ordered", False):
            flagged.append(panel["sample_id"])
    return flagged

if __name__ == "__main__":
    ref = {"potassium": (4.2, 0.4), "sodium": (140.0, 2.0)}
    s1 = {"sample_id": "S1", "analytes": {"potassium": 5.6, "sodium": 147.0}, "fasting_exempt": False, "hemolysis_index": 10.0}
    s2 = {"sample_id": "S2", "analytes": {"potassium": 4.3, "sodium": 140.5}, "fasting_exempt": False, "hemolysis_index": 10.0}
    assert flag_anomalous_lab_panels([s1, s2], ref) == ["S1"]
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 7",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v7.0-expansion",
        "programs": BATCH7_PROGRAMS,
    },
]

def read_existing_manifest():
    """Existing manifest rows keyed by program_id; fails on duplicates."""
    if not MANIFEST_PATH.exists():
        return {}

    with MANIFEST_PATH.open("r", newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        if reader.fieldnames != MANIFEST_COLUMNS:
            raise SystemExit(
                f"Unexpected manifest header in {MANIFEST_PATH}: "
                f"{reader.fieldnames}"
            )

        existing = {}
        for row in reader:
            if None in row or None in row.values():
                raise SystemExit(
                    f"Malformed manifest row at line {reader.line_num} "
                    f"of {MANIFEST_PATH}: wrong number of fields."
                )
            pid = row["program_id"].strip()
            if pid in existing:
                raise SystemExit(
                    f"Manifest already contains duplicate program_id {pid}."
                )
            existing[pid] = {k: (v or "").strip() for k, v in row.items()}

    return existing


def normalized_task(text):
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def program_profile(code):
    tree = ast.parse(code)
    return {
        "ast_hash": hashlib.sha256(ast.dump(tree).encode("utf-8")).hexdigest(),
        "functions": {
            node.name for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        },
        "shape": [type(node).__name__ for node in ast.walk(tree)],
    }


def check_uniqueness(new_programs, existing_manifest):
    """
    Reasons a new program repeats another program in the corpus or in the
    same run:
    - the same task description (ignoring case and punctuation);
    - a shared top-level function name;
    - an identical AST (identical code apart from comments and formatting);
    - an AST node-type sequence whose difflib similarity is at least
      STRUCTURAL_SIMILARITY_LIMIT (catches renamed copies).

    Returns (problems, closest) where closest is the highest similarity
    found as (score, new_id, other_id).
    """
    profiles = {
        path.stem: program_profile(path.read_text(encoding="utf-8"))
        for path in sorted(PROGRAMS_DIR.glob("*.py"))
    }
    tasks = {
        pid: normalized_task(row["task_description"])
        for pid, row in existing_manifest.items()
    }

    problems = []
    closest = (0.0, None, None)

    for pid, task, code in new_programs:
        profile = program_profile(code)
        task_key = normalized_task(task)

        for other_id, other_task in tasks.items():
            if other_id != pid and other_task == task_key:
                problems.append(f"{pid} repeats the task of {other_id}: {task!r}")

        for other_id, other in profiles.items():
            if other_id == pid:
                continue

            if other["ast_hash"] == profile["ast_hash"]:
                problems.append(f"{pid} has the same code as {other_id}")

            shared = profile["functions"] & other["functions"]
            if shared:
                problems.append(
                    f"{pid} reuses function name(s) {sorted(shared)} "
                    f"from {other_id}"
                )

            matcher = difflib.SequenceMatcher(
                None, profile["shape"], other["shape"], autojunk=False
            )
            # Upper bounds; skip pairs that cannot raise the closest score
            # or reach the limit.
            bound = min(closest[0], STRUCTURAL_SIMILARITY_LIMIT)
            if matcher.real_quick_ratio() < bound:
                continue
            if matcher.quick_ratio() < bound:
                continue

            score = matcher.ratio()
            if score > closest[0]:
                closest = (score, pid, other_id)
            if score >= STRUCTURAL_SIMILARITY_LIMIT:
                problems.append(
                    f"{pid} is structurally near-identical to {other_id} "
                    f"(similarity {score:.3f})"
                )

        profiles[pid] = profile
        tasks[pid] = task_key

    return problems, closest


def main():
    existing_manifest = read_existing_manifest()

    planned = []
    conflicts = []
    seen_ids = set()

    for batch in BATCHES:
        for pid, data in sorted(batch["programs"].items()):
            if pid in seen_ids:
                raise SystemExit(f"{pid} is defined in more than one batch.")
            seen_ids.add(pid)
            filepath, code, row, program_conflicts = plan_program(
                pid, data, batch, existing_manifest
            )
            conflicts.extend(program_conflicts)
            planned.append((pid, filepath, code, row))

    if conflicts:
        raise SystemExit(
            "Nothing was written. Resolve these conflicts first:\n- "
            + "\n- ".join(conflicts)
        )

    new_programs = [
        (pid, row["task_description"], code)
        for pid, filepath, code, row in planned
        if not filepath.exists()
    ]

    if new_programs:
        problems, closest = check_uniqueness(new_programs, existing_manifest)

        if problems:
            raise SystemExit(
                "Nothing was written. These new programs repeat existing "
                "ones:\n- " + "\n- ".join(problems)
            )

        score, new_id, other_id = closest
        print(
            f"Uniqueness check passed for {len(new_programs)} new programs; "
            f"highest structural similarity {score:.3f} "
            f"({new_id} vs {other_id}), limit "
            f"{STRUCTURAL_SIMILARITY_LIMIT}."
        )

    write_planned(planned, existing_manifest)


def plan_program(pid, data, batch, existing_manifest):
    filename = f"{pid}.py"
    filepath = PROGRAMS_DIR / filename
    code = data["code"].lstrip()
    conflicts = []

    # AST syntax parsing verification
    ast.parse(code)

    row = dict(zip(MANIFEST_COLUMNS, [
        pid,
        filename,
        data["domain"],
        data["task"],
        data["category"],
        batch["model_id"],
        batch["prompt_version"],
        batch["batch_id"],
        "True",
        "ACCEPTED"
    ]))

    if filepath.exists() and filepath.read_text(encoding="utf-8") != code:
        conflicts.append(f"{filepath} exists with different content")

    existing_row = existing_manifest.get(pid)
    if existing_row is not None and existing_row != row:
        differing = [
            column for column in MANIFEST_COLUMNS
            if existing_row.get(column) != row[column]
        ]
        conflicts.append(
            f"{pid} is already in the manifest with different "
            f"{differing}"
        )

    return filepath, code, row, conflicts


def write_planned(planned, existing_manifest):
    PROGRAMS_DIR.mkdir(parents=True, exist_ok=True)

    written_files = 0
    new_rows = []

    for pid, filepath, code, row in planned:
        if not filepath.exists():
            filepath.write_text(code, encoding="utf-8")
            written_files += 1

        if pid not in existing_manifest:
            new_rows.append(row)

    print(
        f"Verified {len(planned)} programs; wrote {written_files} new "
        f"program files; {len(planned) - written_files} already existed "
        "with identical content."
    )

    if new_rows:
        needs_header = not MANIFEST_PATH.exists()
        needs_newline = (
            not needs_header
            and MANIFEST_PATH.read_bytes()[-1:] not in (b"", b"\n")
        )

        with MANIFEST_PATH.open("a", newline="", encoding="utf-8") as f:
            if needs_newline:
                f.write("\n")
            writer = csv.DictWriter(f, fieldnames=MANIFEST_COLUMNS)
            if needs_header:
                writer.writeheader()
            writer.writerows(new_rows)

    print(
        f"Appended {len(new_rows)} new manifest rows; "
        f"{len(planned) - len(new_rows)} program IDs were already present. "
        f"Manifest: {MANIFEST_PATH}"
    )

if __name__ == "__main__":
    main()