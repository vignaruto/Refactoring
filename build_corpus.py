"""
build_corpus.py
Writes the Batch 6 (P0251-P0300) programs into program_corpus/programs and
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

BATCH6_PROGRAMS = {
    # 1. NONE (8 programs: P0251 - P0258)
    "P0251": {
        "domain": "Numerical Computation",
        "task": "Modular exponentiation by repeated squaring",
        "category": "None",
        "code": '''def modular_power(base: int, exponent: int, modulus: int) -> int:
    if modulus == 1:
        return 0
    result = 1
    base = base % modulus
    while exponent > 0:
        if exponent % 2 == 1:
            result = (result * base) % modulus
        base = (base * base) % modulus
        exponent //= 2
    return result

if __name__ == "__main__":
    assert modular_power(4, 13, 497) == 445
    assert modular_power(2, 10, 1000) == 24
    assert modular_power(7, 0, 13) == 1
'''
    },
    "P0252": {
        "domain": "String Processing & Text Analysis",
        "task": "Caesar cipher letter shifting that preserves case and punctuation",
        "category": "None",
        "code": '''def caesar_shift(text: str, shift: int) -> str:
    shifted = []
    for char in text:
        if char.isupper():
            base = ord("A")
        elif char.islower():
            base = ord("a")
        else:
            shifted.append(char)
            continue
        offset = (ord(char) - base + shift) % 26
        shifted.append(chr(base + offset))
    return "".join(shifted)

if __name__ == "__main__":
    assert caesar_shift("Hello, World!", 3) == "Khoor, Zruog!"
    assert caesar_shift("xyz", 3) == "abc"
    assert caesar_shift(caesar_shift("Round Trip", 11), -11) == "Round Trip"
'''
    },
    "P0253": {
        "domain": "Searching and Sorting",
        "task": "Counting sort for bounded non-negative integers",
        "category": "None",
        "code": '''def counting_sort(values: list[int], max_value: int) -> list[int]:
    counts = [0] * (max_value + 1)
    for value in values:
        counts[value] += 1
    ordered = []
    for value, count in enumerate(counts):
        ordered.extend([value] * count)
    return ordered

if __name__ == "__main__":
    assert counting_sort([3, 1, 4, 1, 5, 9, 2, 6], 9) == [1, 1, 2, 3, 4, 5, 6, 9]
    assert counting_sort([], 5) == []
'''
    },
    "P0254": {
        "domain": "Data Aggregation and Statistics",
        "task": "Median absolute deviation as a robust spread estimate",
        "category": "None",
        "code": '''def median(values: list[float]) -> float:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2 == 1:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2.0

def median_absolute_deviation(values: list[float]) -> float:
    if not values:
        raise ValueError("values must not be empty")
    center = median(values)
    deviations = [abs(value - center) for value in values]
    return median(deviations)

if __name__ == "__main__":
    assert median_absolute_deviation([1, 1, 2, 2, 4, 6, 9]) == 1
    assert median_absolute_deviation([5.0]) == 0.0
'''
    },
    "P0255": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Group normalized words into a dictionary keyed by initial letter",
        "category": "None",
        "code": '''def group_words_by_initial(words: list[str]) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for word in words:
        cleaned = word.strip().lower()
        if not cleaned:
            continue
        groups.setdefault(cleaned[0], []).append(cleaned)
    return groups

if __name__ == "__main__":
    assert group_words_by_initial(["Apple", "avocado", "Banana", " "]) == {"a": ["apple", "avocado"], "b": ["banana"]}
    assert group_words_by_initial([]) == {}
'''
    },
    "P0256": {
        "domain": "Graph or Tree Traversal",
        "task": "Compute in-degree and out-degree of every node from a directed edge list",
        "category": "None",
        "code": '''def degree_counts(edges: list[tuple[str, str]]) -> dict[str, tuple[int, int]]:
    ins: dict[str, int] = {}
    outs: dict[str, int] = {}
    for source, target in edges:
        outs[source] = outs.get(source, 0) + 1
        ins[target] = ins.get(target, 0) + 1
    degrees = {}
    for node in sorted(set(ins) | set(outs)):
        degrees[node] = (ins.get(node, 0), outs.get(node, 0))
    return degrees

if __name__ == "__main__":
    assert degree_counts([("a", "b"), ("a", "c"), ("c", "a")]) == {"a": (1, 2), "b": (1, 0), "c": (1, 1)}
    assert degree_counts([]) == {}
'''
    },
    "P0257": {
        "domain": "Inventory and Record Management",
        "task": "Weighted average unit cost across stock receipts",
        "category": "None",
        "code": '''def weighted_average_cost(receipts: list[tuple[int, float]]) -> float:
    total_units = 0
    total_value = 0.0
    for units, unit_cost in receipts:
        if units <= 0:
            raise ValueError("receipt units must be positive")
        total_units += units
        total_value += units * unit_cost
    if total_units == 0:
        return 0.0
    return round(total_value / total_units, 4)

if __name__ == "__main__":
    assert weighted_average_cost([(10, 2.0), (30, 4.0)]) == 3.5
    assert weighted_average_cost([]) == 0.0
'''
    },
    "P0258": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Round-robin CPU scheduling completion times with a fixed quantum",
        "category": "None",
        "code": '''from collections import deque

def round_robin_completion(bursts: dict[str, int], quantum: int) -> dict[str, int]:
    queue = deque(bursts.items())
    clock = 0
    finished: dict[str, int] = {}
    while queue:
        name, remaining = queue.popleft()
        run = min(quantum, remaining)
        clock += run
        if remaining > run:
            queue.append((name, remaining - run))
        else:
            finished[name] = clock
    return finished

if __name__ == "__main__":
    assert round_robin_completion({"A": 5, "B": 2, "C": 4}, 2) == {"B": 4, "C": 10, "A": 11}
'''
    },

    # 2. LONG STATEMENT ONLY (6 programs: P0259 - P0264)
    "P0259": {
        "domain": "Numerical Computation",
        "task": "Haversine great-circle distance between two coordinates",
        "category": "Long statement only",
        "code": '''import math

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    earth_radius_km = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2.0) ** 2
    return 2.0 * earth_radius_km * math.asin(math.sqrt(a))

if __name__ == "__main__":
    assert haversine_distance_km(0.0, 0.0, 0.0, 0.0) == 0.0
    assert abs(haversine_distance_km(0.0, 0.0, 0.0, 1.0) - 111.195) < 0.01
'''
    },
    "P0260": {
        "domain": "Data Aggregation and Statistics",
        "task": "Cohen's d effect size with pooled standard deviation",
        "category": "Long statement only",
        "code": '''import math

def cohens_d_effect_size(group_a: list[float], group_b: list[float]) -> float:
    n_a, n_b = len(group_a), len(group_b)
    if n_a < 2 or n_b < 2:
        raise ValueError("each group needs at least two observations")
    mean_a = sum(group_a) / n_a
    mean_b = sum(group_b) / n_b
    var_a = sum((x - mean_a) ** 2 for x in group_a) / (n_a - 1)
    var_b = sum((x - mean_b) ** 2 for x in group_b) / (n_b - 1)
    pooled_sd = math.sqrt(((n_a - 1) * var_a + (n_b - 1) * var_b) / (n_a + n_b - 2))
    return (mean_a - mean_b) / pooled_sd

if __name__ == "__main__":
    assert cohens_d_effect_size([2.0, 4.0, 6.0], [1.0, 3.0, 5.0]) == 0.5
'''
    },
    "P0261": {
        "domain": "String Processing & Text Analysis",
        "task": "Keystroke-level model estimate of time to type and enter a text field",
        "category": "Long statement only",
        "code": '''def keystroke_level_time(text: str, pointing_actions: int, homing_actions: int, mental_preparations: int) -> float:
    keystroke_s = 0.28
    pointing_s = 1.1
    homing_s = 0.4
    mental_s = 1.35
    shifted_keys = sum(1 for char in text if char.isupper() or char in "!@#$%^&*()_+{}|:<>?")
    total_seconds = (len(text) + shifted_keys) * keystroke_s + pointing_actions * pointing_s + homing_actions * homing_s + mental_preparations * mental_s
    return round(total_seconds, 3)

if __name__ == "__main__":
    assert keystroke_level_time("Hi there", 1, 2, 1) == 5.77
    assert keystroke_level_time("", 0, 0, 0) == 0.0
'''
    },
    "P0262": {
        "domain": "Inventory and Record Management",
        "task": "Safety stock and days of cover under joint demand and lead-time variability",
        "category": "Long statement only",
        "code": '''import math

def safety_stock_cover(avg_daily_demand: float, demand_sd: float, avg_lead_time_days: float, lead_time_sd: float, service_z: float) -> tuple[float, float]:
    safety_stock = service_z * math.sqrt(avg_lead_time_days * demand_sd ** 2 + (avg_daily_demand ** 2) * lead_time_sd ** 2)
    cover_days = safety_stock / avg_daily_demand if avg_daily_demand > 0 else 0.0
    return round(safety_stock, 2), round(cover_days, 2)

if __name__ == "__main__":
    assert safety_stock_cover(100.0, 20.0, 4.0, 1.0, 1.65) == (177.71, 1.78)
    assert safety_stock_cover(0.0, 0.0, 4.0, 0.0, 1.65) == (0.0, 0.0)
'''
    },
    "P0263": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Projectile range and apex height from an elevated launch point",
        "category": "Long statement only",
        "code": '''import math

def projectile_range_and_apex(speed_ms: float, angle_deg: float, launch_height_m: float, gravity: float = 9.80665) -> tuple[float, float]:
    theta = math.radians(angle_deg)
    vx = speed_ms * math.cos(theta)
    vy = speed_ms * math.sin(theta)
    flight_time = (vy + math.sqrt(vy ** 2 + 2.0 * gravity * launch_height_m)) / gravity
    apex_height = launch_height_m + vy ** 2 / (2.0 * gravity)
    return round(vx * flight_time, 3), round(apex_height, 3)

if __name__ == "__main__":
    assert projectile_range_and_apex(10.0, 0.0, 0.0) == (0.0, 0.0)
    assert abs(projectile_range_and_apex(10.0, 45.0, 0.0)[0] - 10.197) < 0.01
'''
    },
    "P0264": {
        "domain": "Scheduling and Resource Allocation",
        "task": "PERT three-point duration estimates and variances per task",
        "category": "Long statement only",
        "code": '''def pert_estimates(tasks: dict[str, tuple[float, float, float]]) -> dict[str, tuple[float, float]]:
    estimates = {}
    for name, (optimistic, most_likely, pessimistic) in tasks.items():
        expected = (optimistic + 4.0 * most_likely + pessimistic) / 6.0
        variance = ((pessimistic - optimistic) / 6.0) ** 2
        estimates[name] = (round(expected, 3), round(variance, 3))
    return estimates

if __name__ == "__main__":
    assert pert_estimates({"design": (2.0, 4.0, 6.0)}) == {"design": (4.0, 0.444)}
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0265 - P0270)
    "P0265": {
        "domain": "Searching and Sorting",
        "task": "Insertion sort with element shifting",
        "category": "Nested loop only",
        "code": '''def insertion_sort(values: list[int]) -> list[int]:
    items = list(values)
    for index in range(1, len(items)):
        current = items[index]
        position = index - 1
        while position >= 0 and items[position] > current:
            items[position + 1] = items[position]
            position -= 1
        items[position + 1] = current
    return items

if __name__ == "__main__":
    assert insertion_sort([5, 2, 4, 6, 1, 3]) == [1, 2, 3, 4, 5, 6]
    assert insertion_sort([]) == []
'''
    },
    "P0266": {
        "domain": "Matrix & Grid Operations",
        "task": "Kronecker product of two matrices",
        "category": "Nested loop only",
        "code": '''def kronecker_product(a: list[list[float]], b: list[list[float]]) -> list[list[float]]:
    result = []
    for row_a in a:
        for row_b in b:
            new_row = []
            for value_a in row_a:
                for value_b in row_b:
                    new_row.append(value_a * value_b)
            result.append(new_row)
    return result

if __name__ == "__main__":
    assert kronecker_product([[1, 2], [3, 4]], [[0, 5], [6, 7]]) == [[0, 5, 0, 10], [6, 7, 12, 14], [0, 15, 0, 20], [18, 21, 24, 28]]
'''
    },
    "P0267": {
        "domain": "String Processing & Text Analysis",
        "task": "Naive substring search returning all match positions",
        "category": "Nested loop only",
        "code": '''def naive_find_all(text: str, pattern: str) -> list[int]:
    if not pattern:
        return []
    matches = []
    for start in range(len(text) - len(pattern) + 1):
        offset = 0
        while offset < len(pattern):
            if text[start + offset] != pattern[offset]:
                break
            offset += 1
        if offset == len(pattern):
            matches.append(start)
    return matches

if __name__ == "__main__":
    assert naive_find_all("abracadabra", "abra") == [0, 7]
    assert naive_find_all("aaaa", "aa") == [0, 1, 2]
    assert naive_find_all("abc", "") == []
'''
    },
    "P0268": {
        "domain": "Graph or Tree Traversal",
        "task": "Breadth-first search hop distances from a source node",
        "category": "Nested loop only",
        "code": '''from collections import deque

def bfs_hop_distances(graph: dict[str, list[str]], source: str) -> dict[str, int]:
    distances = {source: 0}
    queue = deque([source])
    while queue:
        node = queue.popleft()
        for neighbor in graph.get(node, []):
            if neighbor not in distances:
                distances[neighbor] = distances[node] + 1
                queue.append(neighbor)
    return distances

if __name__ == "__main__":
    assert bfs_hop_distances({"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": []}, "a") == {"a": 0, "b": 1, "c": 1, "d": 2}
    assert bfs_hop_distances({}, "x") == {"x": 0}
'''
    },
    "P0269": {
        "domain": "Data Aggregation and Statistics",
        "task": "Pearson chi-square statistic for a contingency table",
        "category": "Nested loop only",
        "code": '''def chi_square_statistic(table: list[list[int]]) -> float:
    row_totals = [sum(row) for row in table]
    col_totals = [sum(col) for col in zip(*table)]
    grand_total = sum(row_totals)
    statistic = 0.0
    for i, row in enumerate(table):
        for j, observed in enumerate(row):
            expected = row_totals[i] * col_totals[j] / grand_total
            statistic += (observed - expected) ** 2 / expected
    return round(statistic, 4)

if __name__ == "__main__":
    assert chi_square_statistic([[10, 20], [20, 10]]) == 6.6667
    assert chi_square_statistic([[5, 5], [5, 5]]) == 0.0
'''
    },
    "P0270": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "One-dimensional elementary cellular automaton evolution by rule number",
        "category": "Nested loop only",
        "code": '''def run_elementary_automaton(cells: list[int], rule: int, generations: int) -> list[list[int]]:
    current = list(cells)
    history = [current]
    width = len(current)
    for _ in range(generations):
        following = []
        for i in range(width):
            left = current[(i - 1) % width]
            right = current[(i + 1) % width]
            pattern = (left << 2) | (current[i] << 1) | right
            following.append((rule >> pattern) & 1)
        current = following
        history.append(current)
    return history

if __name__ == "__main__":
    assert run_elementary_automaton([0, 0, 0, 1, 0, 0, 0], 90, 1)[-1] == [0, 0, 1, 0, 1, 0, 0]
    assert len(run_elementary_automaton([1, 0, 1], 30, 3)) == 4
'''
    },

    # 4. COMPLEX CONDITIONAL ONLY (6 programs: P0271 - P0276)
    "P0271": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate dotted-decimal IPv4 address strings",
        "category": "Complex conditional only",
        "code": '''def is_valid_ipv4(address: str) -> bool:
    parts = address.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit() or (len(part) > 1 and part[0] == "0") or int(part) > 255:
            return False
    return True

if __name__ == "__main__":
    assert is_valid_ipv4("192.168.0.1") is True
    assert is_valid_ipv4("256.1.1.1") is False
    assert is_valid_ipv4("10.01.0.1") is False
    assert is_valid_ipv4("1.2.3") is False
'''
    },
    "P0272": {
        "domain": "Numerical Computation",
        "task": "Classify a triangle from three side lengths",
        "category": "Complex conditional only",
        "code": '''def classify_triangle(a: float, b: float, c: float) -> str:
    if a <= 0 or b <= 0 or c <= 0:
        return "invalid"
    if a + b <= c or a + c <= b or b + c <= a:
        return "degenerate"
    if a == b and b == c:
        return "equilateral"
    if a == b or b == c or a == c:
        return "isosceles"
    return "scalene"

if __name__ == "__main__":
    assert classify_triangle(3, 4, 5) == "scalene"
    assert classify_triangle(2, 2, 2) == "equilateral"
    assert classify_triangle(2, 2, 3) == "isosceles"
    assert classify_triangle(1, 2, 3) == "degenerate"
    assert classify_triangle(0, 2, 3) == "invalid"
'''
    },
    "P0273": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Check a meeting slot against working hours, room capacity and blackout periods",
        "category": "Complex conditional only",
        "code": '''def is_meeting_slot_valid(start: int, end: int, capacity: int, attendees: int, blackouts: list[tuple[int, int]]) -> bool:
    if start >= end or start < 9 * 60 or end > 18 * 60:
        return False
    if attendees <= 0 or attendees > capacity:
        return False
    for block_start, block_end in blackouts:
        if start < block_end and block_start < end:
            return False
    return True

if __name__ == "__main__":
    assert is_meeting_slot_valid(600, 660, 8, 5, [(720, 780)]) is True
    assert is_meeting_slot_valid(700, 760, 8, 5, [(720, 780)]) is False
    assert is_meeting_slot_valid(480, 540, 8, 5, []) is False
    assert is_meeting_slot_valid(600, 660, 4, 5, []) is False
'''
    },
    "P0274": {
        "domain": "Inventory and Record Management",
        "task": "Decide whether a stock item needs a hazardous-materials shipping label",
        "category": "Complex conditional only",
        "code": '''def requires_hazmat_label(item: dict[str, float], by_air: bool) -> bool:
    flash_point = item.get("flash_point_c", 100.0)
    volume = item.get("volume_l", 0.0)
    corrosive = bool(item.get("corrosive", False))
    sealed = bool(item.get("sealed", True))
    if (flash_point < 60.0 and volume > 1.0) or (corrosive and not sealed):
        return True
    if by_air and (flash_point < 93.0 or item.get("lithium_wh", 0.0) > 100.0):
        return True
    return False

if __name__ == "__main__":
    assert requires_hazmat_label({"flash_point_c": 20.0, "volume_l": 5.0}, False) is True
    assert requires_hazmat_label({"corrosive": True, "sealed": True}, False) is False
    assert requires_hazmat_label({"lithium_wh": 160.0}, True) is True
    assert requires_hazmat_label({"flash_point_c": 80.0, "volume_l": 2.0}, False) is False
'''
    },
    "P0275": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Validate proleptic Gregorian calendar dates including leap years",
        "category": "Complex conditional only",
        "code": '''def is_valid_gregorian_date(year: int, month: int, day: int) -> bool:
    if year < 1583 or month < 1 or month > 12 or day < 1:
        return False
    if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
        february_days = 29
    else:
        february_days = 28
    if month == 2:
        return day <= february_days
    if month in (4, 6, 9, 11):
        return day <= 30
    return day <= 31

if __name__ == "__main__":
    assert is_valid_gregorian_date(2024, 2, 29) is True
    assert is_valid_gregorian_date(1900, 2, 29) is False
    assert is_valid_gregorian_date(2000, 2, 29) is True
    assert is_valid_gregorian_date(2023, 4, 31) is False
    assert is_valid_gregorian_date(2023, 13, 1) is False
'''
    },
    "P0276": {
        "domain": "Matrix & Grid Operations",
        "task": "Check legality of a chess knight move on an occupied board",
        "category": "Complex conditional only",
        "code": '''def is_legal_knight_move(start: tuple[int, int], end: tuple[int, int], own_pieces: set[tuple[int, int]]) -> bool:
    row, col = end
    d_row = abs(end[0] - start[0])
    d_col = abs(end[1] - start[1])
    if not (0 <= row < 8 and 0 <= col < 8) or end in own_pieces:
        return False
    return (d_row, d_col) in ((1, 2), (2, 1))

if __name__ == "__main__":
    assert is_legal_knight_move((0, 1), (2, 2), set()) is True
    assert is_legal_knight_move((0, 1), (2, 2), {(2, 2)}) is False
    assert is_legal_knight_move((7, 7), (9, 8), set()) is False
    assert is_legal_knight_move((3, 3), (4, 4), set()) is False
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (6 programs: P0277 - P0282)
    "P0277": {
        "domain": "Numerical Computation",
        "task": "Finite-difference Hessian matrix of a multivariate function",
        "category": "Long statement and nested loop",
        "code": '''def shifted_point(point: list[float], i: int, di: int, j: int, dj: int, step: float) -> list[float]:
    moved = list(point)
    moved[i] += di * step
    moved[j] += dj * step
    return moved

def numerical_hessian(func, point: list[float], step: float = 1e-4) -> list[list[float]]:
    n = len(point)
    hessian = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            hessian[i][j] = (func(shifted_point(point, i, 1, j, 1, step)) - func(shifted_point(point, i, 1, j, -1, step)) - func(shifted_point(point, i, -1, j, 1, step)) + func(shifted_point(point, i, -1, j, -1, step))) / (4.0 * step * step)
    return hessian

if __name__ == "__main__":
    h = numerical_hessian(lambda v: v[0] ** 2 + 3.0 * v[0] * v[1] + 2.0 * v[1] ** 2, [0.5, -1.0])
    assert all(abs(h[r][c] - [[2.0, 3.0], [3.0, 4.0]][r][c]) < 1e-3 for r in range(2) for c in range(2))
'''
    },
    "P0278": {
        "domain": "Data Aggregation and Statistics",
        "task": "Mean silhouette coefficient for labelled two-dimensional clusters",
        "category": "Long statement and nested loop",
        "code": '''import math

def mean_silhouette_score(points: list[tuple[float, float]], labels: list[int]) -> float:
    scores = []
    for i, p in enumerate(points):
        same, other = [], {}
        for j, q in enumerate(points):
            if i == j:
                continue
            distance = math.hypot(p[0] - q[0], p[1] - q[1])
            if labels[j] == labels[i]:
                same.append(distance)
            else:
                other.setdefault(labels[j], []).append(distance)
        if not same or not other:
            scores.append(0.0)
            continue
        same_mean = sum(same) / len(same)
        nearest_other_mean = min(sum(dists) / len(dists) for dists in other.values())
        silhouette_value = (nearest_other_mean - same_mean) / max(same_mean, nearest_other_mean)
        scores.append(silhouette_value)
    return round(sum(scores) / len(scores), 4)

if __name__ == "__main__":
    score = mean_silhouette_score([(0, 0), (0, 1), (10, 0), (10, 1)], [0, 0, 1, 1])
    assert 0.89 < score < 0.91
'''
    },
    "P0279": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Lotka-Volterra predator-prey dynamics across independent habitat patches",
        "category": "Long statement and nested loop",
        "code": '''def simulate_patch_lotka_volterra(patches: list[dict[str, float]], steps: int, dt: float) -> list[dict[str, float]]:
    state = [dict(patch) for patch in patches]
    for _ in range(steps):
        for patch in state:
            prey, predators = patch["prey"], patch["predators"]
            prey_change = patch["prey_growth"] * prey - patch["predation_rate"] * prey * predators
            predator_change = patch["conversion_rate"] * prey * predators - patch["predator_death"] * predators
            patch["prey"] = max(0.0, prey + dt * prey_change)
            patch["predators"] = max(0.0, predators + dt * predator_change)
    return state

if __name__ == "__main__":
    result = simulate_patch_lotka_volterra([{"prey": 10.0, "predators": 0.0, "prey_growth": 0.5, "predation_rate": 0.02, "conversion_rate": 0.01, "predator_death": 0.2}, {"prey": 0.0, "predators": 5.0, "prey_growth": 0.5, "predation_rate": 0.02, "conversion_rate": 0.01, "predator_death": 0.2}], 1, 0.1)
    assert abs(result[0]["prey"] - 10.5) < 1e-9 and abs(result[1]["predators"] - 4.9) < 1e-9
'''
    },
    "P0280": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Permutation flow-shop completion times with sequence setup delays",
        "category": "Long statement and nested loop",
        "code": '''def flow_shop_completion_times(processing: list[list[float]], setup: list[list[float]]) -> list[list[float]]:
    jobs, machines = len(processing), len(processing[0])
    completion = [[0.0] * machines for _ in range(jobs)]
    for i in range(jobs):
        for j in range(machines):
            previous_job_done = completion[i - 1][j] if i > 0 else 0.0
            previous_machine_done = completion[i][j - 1] if j > 0 else 0.0
            completion[i][j] = max(previous_job_done + setup[i][j], previous_machine_done) + processing[i][j]
    return completion

if __name__ == "__main__":
    assert flow_shop_completion_times([[3.0, 2.0], [1.0, 4.0]], [[0.0, 0.0], [0.0, 0.0]]) == [[3.0, 5.0], [4.0, 9.0]]
    assert flow_shop_completion_times([[3.0, 2.0], [1.0, 4.0]], [[0.0, 0.0], [1.0, 1.0]])[-1][-1] == 10.0
'''
    },
    "P0281": {
        "domain": "Data Aggregation and Statistics",
        "task": "Aggregate diesel and electric carbon emissions per delivery route leg",
        "category": "Long statement and nested loop",
        "code": '''def aggregate_route_emissions(routes: dict[str, list[dict[str, float]]], grid_kg_per_kwh: float) -> dict[str, float]:
    totals = {}
    for route_name, legs in routes.items():
        route_total = 0.0
        for leg in legs:
            diesel_kg = leg["distance_km"] * leg.get("diesel_l_per_km", 0.0) * 2.68 * (1.0 + 0.1 * leg.get("payload_t", 0.0) / max(1.0, leg.get("capacity_t", 1.0)))
            electric_kg = leg["distance_km"] * leg.get("kwh_per_km", 0.0) * grid_kg_per_kwh
            route_total += diesel_kg + electric_kg
        totals[route_name] = round(route_total, 3)
    return totals

if __name__ == "__main__":
    assert aggregate_route_emissions({"A": [{"distance_km": 100.0, "diesel_l_per_km": 0.3, "capacity_t": 10.0}], "B": [{"distance_km": 50.0, "kwh_per_km": 1.2}]}, 0.5) == {"A": 80.4, "B": 30.0}
'''
    },
    "P0282": {
        "domain": "Numerical Computation",
        "task": "Two-dimensional midpoint-rule integration of a modulated Gaussian surface",
        "category": "Long statement and nested loop",
        "code": '''import math

def midpoint_integrate_surface(x_min: float, x_max: float, y_min: float, y_max: float, nx: int, ny: int) -> float:
    dx = (x_max - x_min) / nx
    dy = (y_max - y_min) / ny
    total = 0.0
    for i in range(nx):
        x = x_min + (i + 0.5) * dx
        for j in range(ny):
            y = y_min + (j + 0.5) * dy
            total += (math.exp(-(x * x + y * y)) * (1.0 + 0.5 * math.cos(3.0 * x) * math.sin(2.0 * y)) + 0.1 * x * y) * dx * dy
    return total

if __name__ == "__main__":
    assert abs(midpoint_integrate_surface(-1.0, 1.0, -1.0, 1.0, 200, 200) - 2.2310) < 1e-3
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0283 - P0288)
    "P0283": {
        "domain": "Numerical Computation",
        "task": "Numerically stable quadratic equation roots with degenerate-case handling",
        "category": "Long statement and complex conditional",
        "code": '''import math

def solve_quadratic(a: float, b: float, c: float) -> tuple[str, tuple[float, ...]]:
    if not math.isfinite(a) or not math.isfinite(b) or not math.isfinite(c):
        raise ValueError("coefficients must be finite")
    if a == 0.0:
        if b == 0.0:
            return ("no_unique_solution", ())
        return ("linear", (-c / b,))
    discriminant = b * b - 4.0 * a * c
    if discriminant < 0.0:
        return ("complex", ())
    numerically_stable_q = -0.5 * (b + math.copysign(math.sqrt(discriminant), b))
    if numerically_stable_q == 0.0:
        return ("real", (0.0, 0.0))
    return ("real", tuple(sorted((numerically_stable_q / a, c / numerically_stable_q))))

if __name__ == "__main__":
    assert solve_quadratic(1.0, -3.0, 2.0) == ("real", (1.0, 2.0))
    assert solve_quadratic(0.0, 2.0, -4.0) == ("linear", (2.0,))
    assert solve_quadratic(1.0, 0.0, 1.0) == ("complex", ())
'''
    },
    "P0284": {
        "domain": "Data Aggregation and Statistics",
        "task": "Weekly gross pay with daily and weekly overtime and exemption rules",
        "category": "Long statement and complex conditional",
        "code": '''def compute_weekly_gross_pay(hours: list[float], hourly_rate: float, is_exempt: bool, is_salaried: bool, union_member: bool, holiday_hours: float) -> float:
    total_hours = sum(hours)
    daily_overtime = sum(max(0.0, h - 8.0) for h in hours)
    if is_exempt or (is_salaried and hourly_rate * 40 >= 1128.0) or not hours:
        return round(hourly_rate * min(total_hours, 40.0), 2)
    weekly_overtime = max(0.0, total_hours - 40.0)
    overtime_hours = max(daily_overtime, weekly_overtime)
    premium_multiplier = 1.75 if union_member and holiday_hours > 0 else 1.5
    gross_pay = hourly_rate * (total_hours - overtime_hours) + hourly_rate * premium_multiplier * overtime_hours + hourly_rate * holiday_hours
    return round(gross_pay, 2)

if __name__ == "__main__":
    assert compute_weekly_gross_pay([8, 8, 8, 8, 10], 20.0, False, False, False, 0.0) == 860.0
    assert compute_weekly_gross_pay([9, 9, 9, 9, 9], 20.0, True, False, False, 0.0) == 800.0
'''
    },
    "P0285": {
        "domain": "String Processing & Text Analysis",
        "task": "HTTP response cache freshness lifetime from Cache-Control headers",
        "category": "Long statement and complex conditional",
        "code": '''def http_freshness_seconds(status: int, headers: dict[str, str], shared_cache: bool, response_age_s: int) -> int:
    cache_control = headers.get("cache-control", "").lower()
    if "no-store" in cache_control or ("private" in cache_control and shared_cache) or status not in (200, 203, 204, 301, 404, 410):
        return 0
    directives = {}
    for part in cache_control.split(","):
        key, _, value = part.strip().partition("=")
        directives[key] = value
    if shared_cache and "s-maxage" in directives:
        lifetime = int(directives["s-maxage"])
    elif "max-age" in directives:
        lifetime = int(directives["max-age"])
    else:
        lifetime = int(0.1 * max(0, int(headers.get("date-epoch", "0")) - int(headers.get("last-modified-epoch", "0"))))
    return max(0, lifetime - response_age_s)

if __name__ == "__main__":
    assert http_freshness_seconds(200, {"cache-control": "public, max-age=600"}, False, 100) == 500
    assert http_freshness_seconds(200, {"cache-control": "no-store"}, False, 0) == 0
    assert http_freshness_seconds(200, {"date-epoch": "10000", "last-modified-epoch": "0"}, True, 0) == 1000
'''
    },
    "P0286": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "HVAC cooling load estimate and compressor stage selection",
        "category": "Long statement and complex conditional",
        "code": '''def hvac_compressor_stages(outdoor_c: float, indoor_c: float, setpoint_c: float, occupants: int, floor_area_m2: float, solar_gain_w: float, max_stages: int) -> int:
    cooling_load_w = 3.2 * floor_area_m2 * max(0.0, outdoor_c - setpoint_c) + 75.0 * occupants + 0.6 * solar_gain_w + 12.0 * floor_area_m2
    if indoor_c <= setpoint_c - 0.5 or (outdoor_c < 12.0 and indoor_c < setpoint_c + 2.0) or max_stages <= 0:
        return 0
    stage_capacity_w = 3500.0
    stages = int(-(-cooling_load_w // stage_capacity_w))
    return min(max_stages, max(1, stages))

if __name__ == "__main__":
    assert hvac_compressor_stages(32.0, 26.0, 24.0, 10, 100.0, 2000.0, 4) == 2
    assert hvac_compressor_stages(10.0, 24.5, 24.0, 10, 100.0, 2000.0, 4) == 0
'''
    },
    "P0287": {
        "domain": "Inventory and Record Management",
        "task": "Loading dock detention charge with tiered rates and waiver rules",
        "category": "Long statement and complex conditional",
        "code": '''def dock_detention_charge(arrival_min: int, release_min: int, free_minutes: int, hourly_rate: float, carrier_late: bool, appointment_kept: bool, weather_delay_min: int) -> float:
    if carrier_late or not appointment_kept or release_min <= arrival_min:
        return 0.0
    billable_minutes = max(0, release_min - arrival_min - free_minutes - weather_delay_min)
    tiered_charge = min(billable_minutes, 120) / 60.0 * hourly_rate + max(0, billable_minutes - 120) / 60.0 * hourly_rate * 1.5
    return round(tiered_charge, 2)

if __name__ == "__main__":
    assert dock_detention_charge(0, 300, 120, 60.0, False, True, 0) == 210.0
    assert dock_detention_charge(0, 300, 120, 60.0, True, True, 0) == 0.0
'''
    },
    "P0288": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Conference room booking fee with crowding surcharge and discount eligibility",
        "category": "Long statement and complex conditional",
        "code": '''def conference_room_fee(hours: float, base_rate: float, attendees: int, capacity: int, is_member: bool, is_nonprofit: bool, booked_days_ahead: int, needs_av: bool) -> float:
    if hours <= 0 or attendees > capacity or attendees <= 0:
        raise ValueError("invalid booking")
    av_fee = 45.0 if needs_av else 0.0
    gross = hours * base_rate * (1.0 + 0.25 * max(0, attendees - capacity // 2) / max(1, capacity)) + av_fee * hours
    if (is_member and booked_days_ahead >= 14) or (is_nonprofit and hours >= 4 and not needs_av):
        gross *= 0.8
    return round(gross, 2)

if __name__ == "__main__":
    assert conference_room_fee(2.0, 100.0, 10, 20, False, False, 3, False) == 200.0
    assert conference_room_fee(2.0, 100.0, 10, 20, True, False, 14, False) == 160.0
    assert conference_room_fee(2.0, 100.0, 20, 20, False, False, 3, False) == 225.0
'''
    },

    # 7. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0289 - P0294)
    "P0289": {
        "domain": "Matrix & Grid Operations",
        "task": "Find strict saddle points that are unique row minima and column maxima",
        "category": "Nested loop and complex conditional",
        "code": '''def find_strict_saddle_points(matrix: list[list[int]]) -> list[tuple[int, int]]:
    row_mins = [min(row) for row in matrix]
    col_maxes = [max(col) for col in zip(*matrix)]
    saddles = []
    for i, row in enumerate(matrix):
        for j, value in enumerate(row):
            if value == row_mins[i] and value == col_maxes[j] and row.count(value) == 1:
                saddles.append((i, j))
    return saddles

if __name__ == "__main__":
    assert find_strict_saddle_points([[3, 1, 2], [9, 8, 7], [2, 0, 4]]) == [(1, 2)]
    assert find_strict_saddle_points([[1, 2], [2, 1]]) == []
'''
    },
    "P0290": {
        "domain": "Graph or Tree Traversal",
        "task": "Find mutual follow pairs between active accounts in a social graph",
        "category": "Nested loop and complex conditional",
        "code": '''def find_active_mutual_follows(follows: dict[str, list[str]], active: dict[str, bool]) -> list[tuple[str, str]]:
    pairs = []
    for user, followed in follows.items():
        for other in followed:
            if user < other and user in follows.get(other, []) and active.get(user) and active.get(other):
                pairs.append((user, other))
    return sorted(pairs)

if __name__ == "__main__":
    assert find_active_mutual_follows({"a": ["b", "c"], "b": ["a"], "c": ["a"], "d": ["a"]}, {"a": True, "b": True, "c": False}) == [("a", "b")]
'''
    },
    "P0291": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Detect double-booked rooms among overlapping reservations",
        "category": "Nested loop and complex conditional",
        "code": '''def find_double_bookings(bookings: list[dict[str, int]]) -> list[tuple[int, int]]:
    conflicts = []
    for i in range(len(bookings)):
        for j in range(i + 1, len(bookings)):
            a, b = bookings[i], bookings[j]
            if a["room"] == b["room"] and a["start"] < b["end"] and b["start"] < a["end"]:
                conflicts.append((a["id"], b["id"]))
    return conflicts

if __name__ == "__main__":
    assert find_double_bookings([{"id": 1, "room": 7, "start": 9, "end": 11}, {"id": 2, "room": 7, "start": 10, "end": 12}, {"id": 3, "room": 8, "start": 10, "end": 12}, {"id": 4, "room": 7, "start": 11, "end": 13}]) == [(1, 2), (2, 4)]
'''
    },
    "P0292": {
        "domain": "String Processing & Text Analysis",
        "task": "Find word pairs that differ by exactly one letter substitution excluding stop words",
        "category": "Nested loop and complex conditional",
        "code": '''def find_single_substitution_pairs(words: list[str], stop_words: set[str]) -> list[tuple[str, str]]:
    pairs = []
    unique = sorted(set(words))
    for i, first in enumerate(unique):
        for second in unique[i + 1:]:
            if len(first) != len(second):
                continue
            differences = 0
            for a, b in zip(first, second):
                if a != b:
                    differences += 1
            if differences == 1 and first not in stop_words and second not in stop_words:
                pairs.append((first, second))
    return pairs

if __name__ == "__main__":
    assert find_single_substitution_pairs(["cat", "cot", "cog", "dog", "the", "tho"], {"the"}) == [("cat", "cot"), ("cog", "cot"), ("cog", "dog")]
'''
    },
    "P0293": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Single update step of a falling-sand cellular grid with diagonal sliding",
        "category": "Nested loop and complex conditional",
        "code": '''def step_falling_sand(grid: list[list[str]]) -> list[list[str]]:
    rows, cols = len(grid), len(grid[0])
    cells = [row[:] for row in grid]
    for r in range(rows - 2, -1, -1):
        for c in range(cols):
            if cells[r][c] != "s":
                continue
            if cells[r + 1][c] == ".":
                cells[r + 1][c], cells[r][c] = "s", "."
            elif c > 0 and cells[r + 1][c - 1] == "." and cells[r][c - 1] == ".":
                cells[r + 1][c - 1], cells[r][c] = "s", "."
            elif c + 1 < cols and cells[r + 1][c + 1] == "." and cells[r][c + 1] == ".":
                cells[r + 1][c + 1], cells[r][c] = "s", "."
    return cells

if __name__ == "__main__":
    assert step_falling_sand([[".", "s", "."], [".", ".", "."]]) == [[".", ".", "."], [".", "s", "."]]
    assert step_falling_sand([["s", "."], ["s", "."]]) == [[".", "."], ["s", "s"]]
'''
    },
    "P0294": {
        "domain": "Inventory and Record Management",
        "task": "Match customer returns to eligible original invoice lines",
        "category": "Nested loop and complex conditional",
        "code": '''def match_returns_to_invoice(returns: list[dict], invoice_lines: list[dict]) -> dict[str, str]:
    remaining = {}
    for line in invoice_lines:
        remaining[line["line_id"]] = line["qty"]
    matches = {}
    for item in returns:
        for line in invoice_lines:
            line_id = line["line_id"]
            if line["sku"] == item["sku"] and remaining[line_id] >= item["qty"] and not line.get("final_sale", False):
                remaining[line_id] -= item["qty"]
                matches[item["return_id"]] = line_id
                break
    return matches

if __name__ == "__main__":
    assert match_returns_to_invoice([{"return_id": "R1", "sku": "X", "qty": 2}, {"return_id": "R2", "sku": "Y", "qty": 1}], [{"line_id": "L1", "sku": "X", "qty": 3}, {"line_id": "L2", "sku": "Y", "qty": 1, "final_sale": True}]) == {"R1": "L1"}
'''
    },

    # 8. ALL THREE TARGET ISSUES (6 programs: P0295 - P0300)
    "P0295": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Discrete SIR epidemic across districts with travel coupling and lockdown triggers",
        "category": "All three target issues",
        "code": '''def simulate_district_sir(districts: list[dict[str, float]], travel: list[list[float]], days: int, lockdown_threshold: float) -> list[dict[str, float]]:
    state = [dict(district) for district in districts]
    for _ in range(days):
        imported = [0.0] * len(state)
        for i, source in enumerate(state):
            for j, target in enumerate(state):
                if i != j and travel[i][j] > 0.0 and not source.get("locked", False) and not target.get("locked", False):
                    imported[j] += travel[i][j] * source["infected"] / max(1.0, source["population"])
        for k, d in enumerate(state):
            new_infections = min(d["susceptible"], d["beta"] * d["susceptible"] * (d["infected"] + imported[k]) / max(1.0, d["population"]))
            recoveries = d["gamma"] * d["infected"]
            d["susceptible"] -= new_infections
            d["infected"] += new_infections - recoveries
            d["recovered"] += recoveries
            if d["infected"] / max(1.0, d["population"]) > lockdown_threshold:
                d["locked"] = True
    return state

if __name__ == "__main__":
    result = simulate_district_sir([{"susceptible": 990.0, "infected": 10.0, "recovered": 0.0, "population": 1000.0, "beta": 0.3, "gamma": 0.1}], [[0.0]], 1, 0.5)
    assert abs(result[0]["susceptible"] - 987.03) < 1e-9 and abs(result[0]["infected"] - 11.97) < 1e-9
    assert abs(sum(result[0][key] for key in ("susceptible", "infected", "recovered")) - 1000.0) < 1e-9
'''
    },
    "P0296": {
        "domain": "Matrix & Grid Operations",
        "task": "Coral reef bleaching alert levels from degree heating weeks over a sea temperature grid",
        "category": "All three target issues",
        "code": '''def coral_bleaching_alerts(sst_weekly: list[list[list[float]]], climatology: list[list[float]], reef_mask: list[list[bool]]) -> list[tuple[int, int, int]]:
    alerts = []
    for r, row in enumerate(sst_weekly):
        for c, weekly in enumerate(row):
            if not reef_mask[r][c]:
                continue
            maximum_monthly_mean = climatology[r][c]
            degree_heating_weeks = 0.0
            for temperature in weekly[-12:]:
                hotspot = temperature - maximum_monthly_mean
                if hotspot >= 1.0:
                    degree_heating_weeks += hotspot
            latest_hotspot = weekly[-1] - maximum_monthly_mean
            alert_level = 2 if degree_heating_weeks >= 8.0 else 1 if degree_heating_weeks >= 4.0 else 0
            if alert_level > 0 and latest_hotspot > 0.0 and (len(weekly) >= 4 or degree_heating_weeks >= 8.0):
                alerts.append((r, c, alert_level))
    return alerts

if __name__ == "__main__":
    assert coral_bleaching_alerts([[[29.5] * 4, [29.5] * 4]], [[28.0, 28.0]], [[True, False]]) == [(0, 0, 1)]
    assert coral_bleaching_alerts([[[30.5] * 4]], [[28.0]], [[True]]) == [(0, 0, 2)]
'''
    },
    "P0297": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Assign delivery drones to parcels under payload, battery and wind constraints",
        "category": "All three target issues",
        "code": '''def assign_delivery_drones(drones: list[dict[str, float]], parcels: list[dict[str, float]], wind_ms: float) -> dict[str, str]:
    assignments = {}
    used = set()
    for parcel in sorted(parcels, key=lambda p: -p["priority"]):
        for drone in drones:
            if drone["id"] in used:
                continue
            energy_wh = (drone["base_wh_per_km"] + 0.8 * parcel["mass_kg"]) * parcel["distance_km"] * 2.0 * (1.0 + 0.04 * wind_ms)
            if parcel["mass_kg"] <= drone["max_payload_kg"] and energy_wh <= drone["battery_wh"] * 0.8 and not (wind_ms > 12.0 and parcel["fragile"]):
                assignments[parcel["id"]] = drone["id"]
                used.add(drone["id"])
                break
    return assignments

if __name__ == "__main__":
    drones = [{"id": "D1", "base_wh_per_km": 10.0, "max_payload_kg": 2.0, "battery_wh": 100.0}, {"id": "D2", "base_wh_per_km": 15.0, "max_payload_kg": 5.0, "battery_wh": 400.0}]
    parcels = [{"id": "P1", "mass_kg": 3.0, "distance_km": 5.0, "priority": 2, "fragile": False}, {"id": "P2", "mass_kg": 1.0, "distance_km": 2.0, "priority": 1, "fragile": False}]
    assert assign_delivery_drones(drones, parcels, 0.0) == {"P1": "D2", "P2": "D1"}
'''
    },
    "P0298": {
        "domain": "Inventory and Record Management",
        "task": "Audit controlled-substance cabinet counts across hospital wards",
        "category": "All three target issues",
        "code": '''def audit_controlled_substances(wards: list[dict], tolerance_pct: float) -> list[tuple[str, str, str]]:
    findings = []
    for ward in wards:
        for cabinet in ward["cabinets"]:
            for drug in cabinet["drugs"]:
                expected = drug["opening"] + drug["received"] - drug["dispensed"] - drug["wasted_witnessed"]
                discrepancy_pct = abs(drug["counted"] - expected) / max(1.0, expected) * 100.0
                if discrepancy_pct > tolerance_pct and drug["schedule"] <= 2 and not cabinet.get("recount_pending", False):
                    findings.append((ward["name"], cabinet["id"], drug["name"]))
    return findings

if __name__ == "__main__":
    morphine = {"name": "morphine", "opening": 20, "received": 10, "dispensed": 5, "wasted_witnessed": 1, "counted": 20, "schedule": 2}
    fentanyl = {"name": "fentanyl", "opening": 20, "received": 10, "dispensed": 5, "wasted_witnessed": 1, "counted": 24, "schedule": 2}
    assert audit_controlled_substances([{"name": "ICU", "cabinets": [{"id": "C1", "drugs": [morphine, fentanyl]}]}], 5.0) == [("ICU", "C1", "morphine")]
'''
    },
    "P0299": {
        "domain": "Numerical Computation",
        "task": "Grid search of PI controller gains for a first-order plant step response",
        "category": "All three target issues",
        "code": '''def search_stable_pi_gains(kp_values: list[float], ki_values: list[float], plant_gain: float, time_constant: float, dt: float, steps: int) -> list[tuple[float, float]]:
    stable = []
    for kp in kp_values:
        for ki in ki_values:
            output, integral, peak = 0.0, 0.0, 0.0
            for _ in range(steps):
                error = 1.0 - output
                integral += error * dt
                output += dt * (plant_gain * (kp * error + ki * integral) - output) / time_constant
                peak = max(peak, output)
            overshoot = max(0.0, peak - 1.0)
            if abs(1.0 - output) < 0.02 and overshoot < 0.2 and kp > 0.0:
                stable.append((kp, ki))
    return stable

if __name__ == "__main__":
    gains = search_stable_pi_gains([1.0, 2.0], [0.0, 1.0], 1.0, 1.0, 0.01, 2000)
    assert (1.0, 0.0) not in gains and (2.0, 1.0) in gains
'''
    },
    "P0300": {
        "domain": "Data Aggregation and Statistics",
        "task": "Flag online sellers with burst five-star reviews and unverified purchase signals",
        "category": "All three target issues",
        "code": '''def flag_suspicious_sellers(sellers: list[dict], burst_window_hours: float) -> list[str]:
    flagged = []
    for seller in sellers:
        reviews = sorted(seller["reviews"], key=lambda r: r["hour"])
        burst_count = 0
        for i, review in enumerate(reviews):
            for later in reviews[i + 1:]:
                if later["hour"] - review["hour"] <= burst_window_hours and later["rating"] == 5 and review["rating"] == 5:
                    burst_count += 1
        unverified_share = sum(1 for r in reviews if not r["verified_purchase"]) / max(1, len(reviews))
        suspicion_score = 0.5 * min(1.0, burst_count / 10.0) + 0.3 * unverified_share + 0.2 * (1.0 if seller["account_age_days"] < 30 else 0.0)
        if suspicion_score >= 0.5 or (burst_count >= 5 and unverified_share > 0.5):
            flagged.append(seller["id"])
    return flagged

if __name__ == "__main__":
    burst = [{"hour": 0.1 * k, "rating": 5, "verified_purchase": False} for k in range(6)]
    spaced = [{"hour": 10.0 * k, "rating": 4, "verified_purchase": True} for k in range(3)]
    assert flag_suspicious_sellers([{"id": "S1", "account_age_days": 10, "reviews": burst}, {"id": "S2", "account_age_days": 400, "reviews": spaced}], 1.0) == ["S1"]
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 6",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v6.0-expansion",
        "programs": BATCH6_PROGRAMS,
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