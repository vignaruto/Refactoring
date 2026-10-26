"""
build_corpus.py
Writes the Batch 16 (P0751-P0800) programs into program_corpus/programs and
appends their rows to program_corpus/manifest.csv. Earlier batches are already
in the corpus and are not rebuilt by this script.

Reruns are safe: identical existing files and manifest rows are skipped, and
any conflicting file or metadata stops the run before anything is written.
New programs must not repeat an existing program (see check_uniqueness) and
must fit the refactoring pipeline (see check_architecture_fit).
"""

import ast
import contextlib
import csv
import difflib
import hashlib
import io
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

# The rule-generated labels (generate_dataset.py) each intended_category must
# produce, so manifest categories agree with dataset.csv.
CATEGORY_LABELS = {
    "None": set(),
    "Long statement only": {"long_statement"},
    "Nested loop only": {"nested_loop"},
    "Complex conditional only": {"complex_conditional"},
    "Long statement and nested loop": {"long_statement", "nested_loop"},
    "Long statement and complex conditional": {
        "long_statement", "complex_conditional",
    },
    "Nested loop and complex conditional": {
        "nested_loop", "complex_conditional",
    },
    "All three target issues": {
        "long_statement", "nested_loop", "complex_conditional",
    },
}

DOMAINS = {
    "Numerical Computation",
    "String Processing & Text Analysis",
    "Searching and Sorting",
    "Lists, Tuples, Dictionaries, and Sets",
    "Graph or Tree Traversal",
    "Scheduling and Resource Allocation",
    "Small Simulation and Rule-based Systems",
    "Matrix & Grid Operations",
    "Data Aggregation and Statistics",
    "Inventory and Record Management",
}

# Names transformation.py introduces when it rewrites code.
RESERVED_NAMES = {"_temp1", "_temp2", "_condition"}

BATCH16_PROGRAMS = {
    # 1. NONE (7 programs: P0751 - P0757)
    "P0751": {
        "domain": "Numerical Computation",
        "task": "Greedy Egyptian-fraction decomposition into distinct unit fractions",
        "category": "None",
        "code": '''from fractions import Fraction


def egyptian_fractions(numerator: int, denominator: int) -> list[int]:
    remaining = Fraction(numerator, denominator)
    parts = []
    while remaining > 0:
        unit = -(-remaining.denominator // remaining.numerator)
        parts.append(unit)
        remaining -= Fraction(1, unit)
    return parts


if __name__ == "__main__":
    assert egyptian_fractions(4, 13) == [4, 18, 468]
    assert egyptian_fractions(2, 3) == [2, 6]
'''
    },
    "P0752": {
        "domain": "String Processing & Text Analysis",
        "task": "Mask all but the last few digits of an account number, keeping separators",
        "category": "None",
        "code": '''def mask_digits(token: str, keep: int = 4, mask: str = "*") -> str:
    digits = [ch for ch in token if ch.isdigit()]
    hide = max(len(digits) - keep, 0)
    out = []
    seen = 0
    for ch in token:
        if ch.isdigit():
            out.append(mask if seen < hide else ch)
            seen += 1
        else:
            out.append(ch)
    return "".join(out)


if __name__ == "__main__":
    assert mask_digits("1234-5678-9012") == "****-****-9012"
    assert mask_digits("12") == "12"
'''
    },
    "P0753": {
        "domain": "Searching and Sorting",
        "task": "Three-way partition of a list around a pivot value",
        "category": "None",
        "code": '''def three_way_partition(values, pivot):
    items = list(values)
    low, mid, high = 0, 0, len(items) - 1
    while mid <= high:
        if items[mid] < pivot:
            items[low], items[mid] = items[mid], items[low]
            low += 1
            mid += 1
        elif items[mid] > pivot:
            items[mid], items[high] = items[high], items[mid]
            high -= 1
        else:
            mid += 1
    return items, low, high

if __name__ == "__main__":
    values = [3, 1, 2, 3, 5, 0]
    items, low, high = three_way_partition(values, 3)
    assert all(v < 3 for v in items[:low])
    assert items[low:high + 1] == [3, 3]
    assert all(v > 3 for v in items[high + 1:])
'''
    },
    "P0754": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Split a list into fixed-size padded tuples and undo the padding",
        "category": "None",
        "code": '''def chunk_padded(items, size, fill=None):
    chunks = []
    for start in range(0, len(items), size):
        chunk = list(items[start:start + size])
        chunk.extend([fill] * (size - len(chunk)))
        chunks.append(tuple(chunk))
    return chunks

def unchunk(chunks, fill=None):
    flat = [x for chunk in chunks for x in chunk]
    while flat and flat[-1] == fill:
        flat.pop()
    return flat

if __name__ == "__main__":
    chunks = chunk_padded([1, 2, 3, 4, 5], 2)
    assert chunks == [(1, 2), (3, 4), (5, None)]
    assert unchunk(chunks) == [1, 2, 3, 4, 5]
'''
    },
    "P0755": {
        "domain": "Graph or Tree Traversal",
        "task": "Height of a tree and its leaves in left-to-right order, recursively",
        "category": "None",
        "code": '''def tree_height(children: dict, node) -> int:
    kids = children.get(node, [])
    if not kids:
        return 0
    return 1 + max(tree_height(children, k) for k in kids)


def leaf_names(children: dict, node) -> list:
    kids = children.get(node, [])
    if not kids:
        return [node]
    leaves = []
    for kid in kids:
        leaves.extend(leaf_names(children, kid))
    return leaves


if __name__ == "__main__":
    children = {"r": ["a", "b"], "a": ["c", "d"]}
    assert tree_height(children, "r") == 2
    assert leaf_names(children, "r") == ["c", "d", "b"]
'''
    },
    "P0756": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Job completion times on one machine and mean flow time, SPT or as given",
        "category": "None",
        "code": '''def completion_times(durations: list[int]) -> list[int]:
    times, clock = [], 0
    for d in durations:
        clock += d
        times.append(clock)
    return times


def mean_flow_time(jobs: list[int], shortest_first: bool = True) -> float:
    order = sorted(jobs) if shortest_first else list(jobs)
    finished = completion_times(order)
    return sum(finished) / len(finished) if finished else 0.0


if __name__ == "__main__":
    assert completion_times([3, 1, 2]) == [3, 4, 6]
    assert abs(mean_flow_time([3, 1, 2]) - 10 / 3) < 1e-9
    assert abs(mean_flow_time([3, 1, 2], False) - 13 / 3) < 1e-9
'''
    },
    "P0757": {
        "domain": "Data Aggregation and Statistics",
        "task": "Median of a stream after each new value using two heaps",
        "category": "None",
        "code": '''import heapq

def running_medians(values):
    low, high = [], []
    medians = []
    for v in values:
        heapq.heappush(low, -v)
        heapq.heappush(high, -heapq.heappop(low))
        if len(high) > len(low):
            heapq.heappush(low, -heapq.heappop(high))
        if len(low) > len(high):
            medians.append(float(-low[0]))
        else:
            medians.append((-low[0] + high[0]) / 2)
    return medians

if __name__ == "__main__":
    assert running_medians([5, 15, 1, 3]) == [5.0, 10.0, 5.0, 4.0]
'''
    },

    # 2. LONG STATEMENT ONLY (7 programs: P0758 - P0764)
    "P0758": {
        "domain": "Numerical Computation",
        "task": "Great-circle distance and initial compass bearing between coordinates",
        "category": "Long statement only",
        "code": '''import math

def great_circle_km(lat1, lon1, lat2, lon2, radius=6371.0):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return round(2 * radius * math.asin(math.sqrt(a)), 3)

def initial_bearing(lat1, lon1, lat2, lon2):
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_lambda = math.radians(lon2 - lon1)
    y = math.sin(d_lambda) * math.cos(phi2)
    x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(d_lambda)
    return round((math.degrees(math.atan2(y, x)) + 360) % 360, 2)

if __name__ == "__main__":
    assert abs(great_circle_km(0, 0, 0, 1) - 111.195) < 0.01
    assert initial_bearing(0, 0, 0, 1) == 90.0
    assert initial_bearing(0, 0, 1, 0) == 0.0
'''
    },
    "P0759": {
        "domain": "String Processing & Text Analysis",
        "task": "Normalise the lines of a postal address block",
        "category": "Long statement only",
        "code": '''def format_address(name, street, city, postcode, country="", attention=""):
    lines = [name.strip().title()]
    if attention:
        lines.append("Attn: " + attention.strip())
    lines.append(street.strip())
    lines.append(f"{city.strip().upper()} {postcode.strip().upper()}".strip())
    if country:
        lines.append(country.strip().upper())
    return [line for line in lines if line]

if __name__ == "__main__":
    name, street = " jane doe", "1 High St"
    city, code = "leeds", "ls1 4ap"
    lines = format_address(name, street, city, code, "uk")
    assert lines == ["Jane Doe", "1 High St", "LEEDS LS1 4AP", "UK"]
'''
    },
    "P0760": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Match a candidate's skill levels against required and nice-to-have skills",
        "category": "Long statement only",
        "code": '''def skill_match(candidate: dict, required: dict, nice: set) -> tuple:
    levels = {s: candidate.get(s, 0) for s in required}
    covered = [s for s in required if levels[s] >= required[s]]
    some = [s for s in required if 0 < levels[s] < required[s]]
    bonus = len(nice & set(candidate))
    score = len(covered) * 10 + len(some) * 4 + bonus * 2 - (len(required) - len(covered) - len(some)) * 5
    return round(score / max(len(required) * 10 + len(nice) * 2, 1) * 100, 1), sorted(set(required) - set(covered))


if __name__ == "__main__":
    candidate = {"py": 3, "sql": 1, "git": 2}
    required = {"py": 2, "sql": 2, "k8s": 1}
    result = skill_match(candidate, required, {"git", "docker"})
    assert result == (32.4, ["k8s", "sql"])
'''
    },
    "P0761": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Heating cost from fabric and ventilation heat loss over some hours",
        "category": "Long statement only",
        "code": '''def heating_cost(areas, u_values, inside_c, outside_c, hours, price_kwh, air_changes=0.5, volume_m3=250):
    fabric_w = sum(a * u for a, u in zip(areas, u_values)) * (inside_c - outside_c)
    ventilation_w = 0.33 * air_changes * volume_m3 * (inside_c - outside_c)
    cost = (fabric_w + ventilation_w) / 1000 * hours * price_kwh
    return round(cost, 2)

if __name__ == "__main__":
    areas, u_values = [10, 20], [2.0, 0.5]
    args = (20, 0, 10, 0.3, 0.5, 100)
    cost = heating_cost(areas, u_values, *args)
    assert cost == 2.79
'''
    },
    "P0762": {
        "domain": "Matrix & Grid Operations",
        "task": "Trace, 3x3 determinant by cofactor expansion and an invertibility test",
        "category": "Long statement only",
        "code": '''def det3(m):
    return m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1]) - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0]) + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])

def trace(m):
    return sum(m[i][i] for i in range(len(m)))

def is_invertible(m, eps=1e-12):
    return abs(det3(m)) > eps

if __name__ == "__main__":
    diagonal = [[2, 0, 0], [0, 3, 0], [0, 0, 4]]
    singular = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    assert det3(diagonal) == 24
    assert trace(diagonal) == 9
    assert not is_invertible(singular)
'''
    },
    "P0763": {
        "domain": "Inventory and Record Management",
        "task": "Landed unit cost after splitting freight by weight and adding insurance",
        "category": "Long statement only",
        "code": '''def allocate_freight(lines, freight_total, insurance_rate=0.01):
    total_weight = sum(qty * unit_weight for _, qty, _, unit_weight in lines)
    costs = {}
    for sku, qty, unit_price, unit_weight in lines:
        share = freight_total * (qty * unit_weight) / total_weight if total_weight else 0.0
        landed = qty * unit_price + share + qty * unit_price * insurance_rate
        costs[sku] = round(landed / qty, 4)
    return costs

if __name__ == "__main__":
    lines = [("a", 10, 2.0, 1.0), ("b", 5, 10.0, 2.0)]
    assert allocate_freight(lines, 40) == {"a": 4.02, "b": 14.1}
'''
    },
    "P0764": {
        "domain": "Scheduling and Resource Allocation",
        "task": "PERT expected project length, its spread and a 95th-percentile finish",
        "category": "Long statement only",
        "code": '''def pert_estimate(tasks):
    total_mean = 0.0
    total_var = 0.0
    for optimistic, most_likely, pessimistic in tasks:
        expected_duration = (optimistic + 4 * most_likely + pessimistic) / 6
        total_mean += expected_duration
        total_var += ((pessimistic - optimistic) / 6) ** 2
    return round(total_mean, 2), round(total_var ** 0.5, 2), round(total_mean + 1.645 * total_var ** 0.5, 2)

if __name__ == "__main__":
    tasks = [(2, 4, 6), (1, 2, 9)]
    assert pert_estimate(tasks) == (7.0, 1.49, 9.45)
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0765 - P0770)
    "P0765": {
        "domain": "String Processing & Text Analysis",
        "task": "Longest run of characters shared by two strings, by dynamic programming",
        "category": "Nested loop only",
        "code": '''def shared_run(a, b):
    best_len, best_end = 0, 0
    prev = [0] * (len(b) + 1)
    for i in range(1, len(a) + 1):
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1] + 1
                if cur[j] > best_len:
                    best_len, best_end = cur[j], i
        prev = cur
    return a[best_end - best_len:best_end]

if __name__ == "__main__":
    assert shared_run("photograph", "tomography") == "ograph"
    assert shared_run("abc", "xyz") == ""
'''
    },
    "P0766": {
        "domain": "Searching and Sorting",
        "task": "Pancake sort using prefix reversals, recording each flip size",
        "category": "Nested loop only",
        "code": '''def prefix_flip_sort(values):
    items = list(values)
    flips = []
    for size in range(len(items), 1, -1):
        biggest = items.index(max(items[:size]))
        if biggest == size - 1:
            continue
        for k in (biggest + 1, size):
            if k > 1:
                items[:k] = items[:k][::-1]
                flips.append(k)
    return items, flips

if __name__ == "__main__":
    assert prefix_flip_sort([3, 1, 2]) == ([1, 2, 3], [3, 2])
    assert prefix_flip_sort([]) == ([], [])
'''
    },
    "P0767": {
        "domain": "Graph or Tree Traversal",
        "task": "Number of walks of length k between every pair of nodes",
        "category": "Nested loop only",
        "code": '''def walks_of_length(adj, k):
    n = len(adj)
    counts = [[int(i == j) for j in range(n)] for i in range(n)]
    for _ in range(k):
        nxt = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                nxt[i][j] = sum(counts[i][m] * adj[m][j] for m in range(n))
        counts = nxt
    return counts

if __name__ == "__main__":
    triangle = [[0, 1, 1], [1, 0, 1], [1, 1, 0]]
    assert walks_of_length(triangle, 2)[0] == [2, 1, 1]
    assert walks_of_length(triangle, 0)[1] == [0, 1, 0]
'''
    },
    "P0768": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Run a one-dimensional elementary cellular automaton by rule number",
        "category": "Nested loop only",
        "code": '''def elementary_automaton(cells, rule, generations):
    history = [list(cells)]
    for _ in range(generations):
        row = history[-1]
        nxt = []
        for i in range(len(row)):
            left = row[i - 1] if i > 0 else 0
            right = row[i + 1] if i < len(row) - 1 else 0
            index = left * 4 + row[i] * 2 + right
            nxt.append((rule >> index) & 1)
        history.append(nxt)
    return history

if __name__ == "__main__":
    history = elementary_automaton([0, 0, 1, 0, 0], 90, 2)
    assert history[1] == [0, 1, 0, 1, 0]
    assert history[2] == [1, 0, 0, 0, 1]
'''
    },
    "P0769": {
        "domain": "Matrix & Grid Operations",
        "task": "Saddle points that are the maximum of their row and minimum of their column",
        "category": "Nested loop only",
        "code": '''def saddle_points(matrix: list[list[int]]) -> list[tuple[int, int]]:
    col_mins = [min(col) for col in zip(*matrix)]
    points = []
    for r, row in enumerate(matrix):
        row_max = max(row)
        for c, value in enumerate(row):
            if value == row_max and value == col_mins[c]:
                points.append((r, c))
    return points


if __name__ == "__main__":
    matrix = [[9, 8, 7], [5, 3, 2], [6, 6, 7]]
    assert saddle_points(matrix) == [(1, 0)]
'''
    },
    "P0770": {
        "domain": "Inventory and Record Management",
        "task": "Closing stock balance per SKU after each day of movements",
        "category": "Nested loop only",
        "code": '''def daily_balances(opening, days):
    balances = dict(opening)
    history = []
    for day, moves in days:
        for sku, change in moves:
            balances[sku] = balances.get(sku, 0) + change
        history.append((day, dict(sorted(balances.items()))))
    return history

if __name__ == "__main__":
    days = [("mon", [("a", -2), ("b", 4)]), ("tue", [("a", 1)])]
    history = daily_balances({"a": 5}, days)
    assert history[0] == ("mon", {"a": 3, "b": 4})
    assert history[1] == ("tue", {"a": 4, "b": 4})
'''
    },

    # 4. COMPLEX CONDITIONAL ONLY (6 programs: P0771 - P0776)
    "P0771": {
        "domain": "Numerical Computation",
        "task": "Whether a float is within tolerance of an integer and finite-sized",
        "category": "Complex conditional only",
        "code": '''import math


def is_near_integer(value: float, abs_tol: float = 1e-9, max_magnitude: float = 1e15) -> bool:
    nearest = round(value) if math.isfinite(value) else 0
    if abs(value) < max_magnitude and abs(value - nearest) <= abs_tol and value == value:
        return True
    return False


if __name__ == "__main__":
    assert is_near_integer(3.0000000001)
    assert not is_near_integer(2.5)
    assert not is_near_integer(float("nan"))
    assert not is_near_integer(1e16)
'''
    },
    "P0772": {
        "domain": "Searching and Sorting",
        "task": "Index of the first value repeated within k positions, ignoring some values",
        "category": "Complex conditional only",
        "code": '''def first_close_duplicate(values, k, ignore=()):
    last_seen = {}
    for i, v in enumerate(values):
        if v not in ignore and v in last_seen and i - last_seen[v] <= k:
            return i
        last_seen[v] = i
    return -1

if __name__ == "__main__":
    values = [1, 2, 3, 1, 2]
    assert first_close_duplicate(values, 2) == -1
    assert first_close_duplicate(values, 3) == 3
    assert first_close_duplicate(values, 3, {1}) == 4
'''
    },
    "P0773": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Check a record against a field schema of types and required flags",
        "category": "Complex conditional only",
        "code": '''def schema_errors(record: dict, schema: dict) -> list[str]:
    errors = []
    for field, (kind, required) in schema.items():
        value = record.get(field)
        if value is None and required:
            errors.append(f"missing {field}")
        elif value is not None and not isinstance(value, kind) or isinstance(value, bool) and kind is int:
            errors.append(f"bad {field}")
    return errors


if __name__ == "__main__":
    schema = {"id": (int, True), "name": (str, True)}
    schema["age"] = (int, False)
    errors = schema_errors({"id": True, "age": "x"}, schema)
    assert errors == ["bad id", "missing name", "bad age"]
    assert schema_errors({"id": 1, "name": "a"}, schema) == []
'''
    },
    "P0774": {
        "domain": "Graph or Tree Traversal",
        "task": "Whether adding an edge keeps a directed graph acyclic",
        "category": "Complex conditional only",
        "code": '''def can_add_edge(graph: dict, src, dst) -> bool:
    if src == dst or src not in graph or dst not in graph:
        return False
    stack, seen = [dst], set()
    while stack:
        node = stack.pop()
        if node == src:
            return False
        if node not in seen:
            seen.add(node)
            stack.extend(graph[node])
    return True


if __name__ == "__main__":
    graph = {"a": ["b"], "b": ["c"], "c": []}
    assert can_add_edge(graph, "a", "c")
    assert not can_add_edge(graph, "c", "a")
    assert not can_add_edge(graph, "a", "a")
    assert not can_add_edge(graph, "a", "z")
'''
    },
    "P0775": {
        "domain": "Data Aggregation and Statistics",
        "task": "Consume samples until the confidence interval is narrow enough",
        "category": "Complex conditional only",
        "code": '''def samples_until_precise(values, target_half_width, min_n=3, z=1.96):
    n, total, sq = 0, 0.0, 0.0
    half_width = float("inf")
    while n < len(values) and (n < min_n or half_width > target_half_width):
        x = values[n]
        n += 1
        total += x
        sq += x * x
        if n > 1:
            variance = max((sq - total * total / n) / (n - 1), 0.0)
            half_width = z * (variance / n) ** 0.5
    return n, round(half_width, 4)

if __name__ == "__main__":
    assert samples_until_precise([10] * 8, 1.0) == (3, 0.0)
    values = [1, 9, 1, 9, 5, 5, 5, 5]
    n, width = samples_until_precise(values, 3.0)
    assert n == 6
    assert abs(width - 2.8628) < 1e-3
'''
    },
    "P0776": {
        "domain": "Inventory and Record Management",
        "task": "Approve or escalate a stock write-off by reason, value and approver level",
        "category": "Complex conditional only",
        "code": '''def approve_write_off(qty, unit_cost, reason, approver_level):
    value = qty * unit_cost
    if reason in ("damaged", "expired") and value <= 500 and approver_level >= 1:
        return "approved"
    if value > 500 and approver_level >= 2 or reason == "audit":
        return "approved"
    return "escalate"

if __name__ == "__main__":
    assert approve_write_off(10, 20, "damaged", 1) == "approved"
    assert approve_write_off(100, 20, "damaged", 1) == "escalate"
    assert approve_write_off(100, 20, "lost", 2) == "approved"
    assert approve_write_off(1, 1, "audit", 0) == "approved"
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (6 programs: P0777 - P0782)
    "P0777": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Understaffed hours per day against hourly demand, with overall coverage",
        "category": "Long statement and nested loop",
        "code": '''def coverage_gaps(shifts, demand):
    gaps = {}
    for day, hourly_need in demand.items():
        for hour, need in enumerate(hourly_need):
            staffed = sum(1 for d, start, end in shifts if d == day and start <= hour < end)
            if staffed < need:
                gaps[(day, hour)] = need - staffed
    coverage = 100 - sum(gaps.values()) * 100 / max(sum(sum(h) for h in demand.values()), 1)
    return gaps, round(coverage, 1)

if __name__ == "__main__":
    shifts = [("mon", 9, 12), ("mon", 10, 11)]
    demand = {"mon": [0] * 9 + [1, 2, 2]}
    assert coverage_gaps(shifts, demand) == ({("mon", 11): 1}, 80.0)
'''
    },
    "P0778": {
        "domain": "Data Aggregation and Statistics",
        "task": "Pearson correlation of two series over each sliding window",
        "category": "Long statement and nested loop",
        "code": '''def windowed_correlation(xs, ys, window):
    out = []
    for start in range(len(xs) - window + 1):
        sx = sy = sxx = syy = sxy = 0.0
        for x, y in zip(xs[start:start + window], ys[start:start + window]):
            sx += x
            sy += y
            sxx += x * x
            syy += y * y
            sxy += x * y
        cov = sxy - sx * sy / window
        denom = ((sxx - sx * sx / window) * (syy - sy * sy / window)) ** 0.5
        out.append(round(cov / denom, 3) if denom else 0.0)
    return out

if __name__ == "__main__":
    assert windowed_correlation([1, 2, 3, 4], [2, 4, 6, 3], 3) == [1.0, -0.327]
'''
    },
    "P0779": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Euler-step predator and prey populations for several scenarios",
        "category": "Long statement and nested loop",
        "code": '''def lotka_volterra_runs(scenarios, steps, dt=0.01):
    finals = []
    for prey, predators, alpha, beta, delta, gamma in scenarios:
        for _ in range(steps):
            prey_change = (alpha * prey - beta * prey * predators) * dt
            predator_change = (delta * prey * predators - gamma * predators) * dt
            prey, predators = max(prey + prey_change, 0.0), max(predators + predator_change, 0.0)
        finals.append((round(prey, 2), round(predators, 2)))
    return finals

if __name__ == "__main__":
    only_prey = (10, 0, 0.1, 0.02, 0.01, 0.1)
    only_predators = (0, 5, 0.1, 0.02, 0.01, 0.1)
    scenarios = [only_prey, only_predators]
    finals = lotka_volterra_runs(scenarios, 100)
    assert finals == [(11.05, 0.0), (0.0, 4.52)]
'''
    },
    "P0780": {
        "domain": "Matrix & Grid Operations",
        "task": "Manhattan distance from every cell to the nearest marked cell, two passes",
        "category": "Long statement and nested loop",
        "code": '''def manhattan_distance_map(grid):
    rows, cols = len(grid), len(grid[0])
    far = rows + cols
    dist = [[0 if grid[r][c] else far for c in range(cols)] for r in range(rows)]
    for r in range(rows):
        for c in range(cols):
            up = dist[r - 1][c] + 1 if r > 0 else far
            left = dist[r][c - 1] + 1 if c > 0 else far
            dist[r][c] = min(dist[r][c], up, left)
    for r in range(rows - 1, -1, -1):
        for c in range(cols - 1, -1, -1):
            down = dist[r + 1][c] + 1 if r < rows - 1 else far
            right = dist[r][c + 1] + 1 if c < cols - 1 else far
            dist[r][c] = min(dist[r][c], down, right)
    return dist

if __name__ == "__main__":
    grid = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    assert manhattan_distance_map(grid) == [[2, 1, 2], [1, 0, 1], [2, 1, 2]]
'''
    },
    "P0781": {
        "domain": "Numerical Computation",
        "task": "Taylor-series sine and cosine table with an accuracy flag per angle",
        "category": "Long statement and nested loop",
        "code": '''import math


def taylor_table(angles: list[float], terms: int = 10) -> list[tuple]:
    rows = []
    for x in angles:
        sin_sum, cos_sum = 0.0, 0.0
        for k in range(terms):
            sin_sum += (-1) ** k * x ** (2 * k + 1) / math.factorial(2 * k + 1)
            cos_sum += (-1) ** k * x ** (2 * k) / math.factorial(2 * k)
        error = abs(sin_sum - math.sin(x)) + abs(cos_sum - math.cos(x))
        rows.append((x, round(sin_sum, 6), round(cos_sum, 6), error < 1e-6))
    return rows


if __name__ == "__main__":
    rows = taylor_table([0.0, 1.0])
    assert rows[0] == (0.0, 0.0, 1.0, True)
    assert rows[1] == (1.0, 0.841471, 0.540302, True)
'''
    },
    "P0782": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Dot product of every pair of sparse term-weight dictionaries",
        "category": "Long statement and nested loop",
        "code": '''def pairwise_dot(vectors):
    names = sorted(vectors)
    result = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            small, large = sorted((vectors[a], vectors[b]), key=len)
            result[(a, b)] = sum(weight * large.get(term, 0) for term, weight in small.items())
    return result

if __name__ == "__main__":
    vectors = {"d1": {"x": 1, "y": 2}, "d2": {"y": 3}}
    vectors["d3"] = {"z": 1}
    result = pairwise_dot(vectors)
    assert result == {("d1", "d2"): 6, ("d1", "d3"): 0, ("d2", "d3"): 0}
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0783 - P0788)
    "P0783": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Approve a shift swap by weekly hours and rest gap, with a fatigue score",
        "category": "Long statement and complex conditional",
        "code": '''def approve_swap(worker_hours, giver, taker, shift_hours, rest_gap, max_weekly=48):
    taker_total = worker_hours.get(taker, 0) + shift_hours
    fatigue_score = taker_total / max_weekly * 70 + max(0, 11 - rest_gap) * 5 + shift_hours * 1.5
    if taker_total <= max_weekly and rest_gap >= 11 and giver != taker:
        return True, round(fatigue_score, 1)
    return False, round(fatigue_score, 1)

if __name__ == "__main__":
    hours = {"a": 30, "b": 40}
    assert approve_swap(hours, "a", "b", 8, 12) == (True, 82.0)
    assert approve_swap(hours, "a", "b", 8, 8) == (False, 97.0)
'''
    },
    "P0784": {
        "domain": "Data Aggregation and Statistics",
        "task": "Grade a data column by blanks, invalid codes and distinct values",
        "category": "Long statement and complex conditional",
        "code": '''def column_quality(values, allowed=None):
    total = len(values)
    blanks = sum(1 for v in values if v in (None, ""))
    distinct = len({v for v in values if v not in (None, "")})
    invalid = sum(1 for v in values if allowed and v not in (None, "") and v not in allowed)
    if total and blanks / total < 0.05 and invalid == 0 or distinct == 1:
        grade = "A"
    elif blanks / max(total, 1) < 0.2:
        grade = "B"
    else:
        grade = "C"
    return grade, round(1 - (blanks + invalid) / max(total, 1), 3), distinct

if __name__ == "__main__":
    assert column_quality(["a", "b", "a"], {"a", "b"}) == ("A", 1.0, 2)
    messy = ["a", "", "x", None, "a"]
    assert column_quality(messy, {"a"}) == ("C", 0.4, 2)
'''
    },
    "P0785": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Autopilot pitch command with a stall and low-altitude recovery mode",
        "category": "Long statement and complex conditional",
        "code": '''def pitch_command(altitude, target_altitude, vertical_speed, airspeed, stall_speed=55.0):
    error = target_altitude - altitude
    command = 0.02 * error - 0.15 * vertical_speed - 0.5 * max(0.0, stall_speed * 1.2 - airspeed)
    if airspeed < stall_speed * 1.1 or altitude < 500 and error < 0 and vertical_speed < -10:
        return "recover", round(command, 2)
    return "track", round(max(-10.0, min(10.0, command)), 2)

if __name__ == "__main__":
    assert pitch_command(1000, 1500, 0, 100) == ("track", 10.0)
    assert pitch_command(400, 300, -20, 100) == ("recover", 1.0)
    assert pitch_command(3000, 3000, 0, 58) == ("recover", -4.0)
'''
    },
    "P0786": {
        "domain": "Matrix & Grid Operations",
        "task": "Magic-square check reporting every line sum when it fails",
        "category": "Long statement and complex conditional",
        "code": '''def magic_square_report(m):
    target = sum(m[0])
    rows_ok = all(sum(row) == target for row in m)
    cols_ok = all(sum(col) == target for col in zip(*m))
    diag = sum(m[i][i] for i in range(len(m)))
    anti = sum(m[i][len(m) - 1 - i] for i in range(len(m)))
    if rows_ok and cols_ok and diag == target and anti == target:
        return True, target
    return False, [sum(row) for row in m] + [sum(col) for col in zip(*m)] + [diag, anti]

if __name__ == "__main__":
    assert magic_square_report([[2, 7, 6], [9, 5, 1], [4, 3, 8]]) == (True, 15)
    assert magic_square_report([[1, 2], [3, 4]]) == (False, [3, 7, 4, 6, 5, 5])
'''
    },
    "P0787": {
        "domain": "String Processing & Text Analysis",
        "task": "Spam score of a message from blocked words, capitals and exclamations",
        "category": "Long statement and complex conditional",
        "code": '''def spam_score(message: str, blocked_words: set) -> tuple:
    words = message.split()
    caps = sum(1 for w in words if len(w) > 2 and w.isupper())
    exclaims = message.count("!")
    cleaned = [w.lower().strip(".,!?") for w in words]
    hits = sum(1 for w in cleaned if w in blocked_words)
    score = hits * 3 + caps * 1.5 + exclaims * 0.5 + (len(message) > 200) * 2 - (len(words) > 50)
    if score >= 6 or hits >= 2 and exclaims > 2 or "http" in message and hits:
        return "spam", score
    return "ham", score


if __name__ == "__main__":
    assert spam_score("FREE money NOW!!!", {"free", "money"}) == ("spam", 10.5)
    assert spam_score("Lunch at noon?", {"free"}) == ("ham", 0)
'''
    },
    "P0788": {
        "domain": "Inventory and Record Management",
        "task": "Markdown discounts for perishable stock near expiry and expected revenue",
        "category": "Long statement and complex conditional",
        "code": '''def markdown_plan(items, today):
    plan = []
    revenue = 0.0
    for sku, qty, price, expiry_day, category in items:
        days_left = expiry_day - today
        if days_left <= 2 and qty > 0 or category == "bakery" and days_left <= 1:
            discount = 0.5
        elif days_left <= 5:
            discount = 0.2
        else:
            discount = 0.0
        revenue += qty * price * (1 - discount) * (0.9 if discount >= 0.5 else 1.0)
        plan.append((sku, discount))
    return plan, round(revenue, 2)

if __name__ == "__main__":
    items = [("milk", 10, 2.0, 12, "dairy")]
    items.append(("bread", 5, 3.0, 11, "bakery"))
    items.append(("cheese", 2, 10.0, 30, "dairy"))
    plan, revenue = markdown_plan(items, 10)
    assert plan == [("milk", 0.5), ("bread", 0.5), ("cheese", 0.0)]
    assert revenue == 35.75
'''
    },

    # 7. ALL THREE TARGET ISSUES (6 programs: P0789 - P0794)
    "P0789": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Give each exam class the smallest suitable free room, with seat utilisation",
        "category": "All three target issues",
        "code": '''def assign_exam_rooms(classes, rooms):
    used = set()
    plan = {}
    for name, students, needs_access in sorted(classes, key=lambda c: -c[1]):
        best = None
        for room, seats, accessible in rooms:
            if room not in used and seats >= students and (accessible or not needs_access):
                if best is None or seats < best[1]:
                    best = (room, seats)
        if best:
            used.add(best[0])
            plan[name] = best[0]
    utilisation = sum(n for c, n, _ in classes if c in plan) / max(sum(s for r, s, _ in rooms if r in used), 1)
    return plan, round(utilisation, 3)

if __name__ == "__main__":
    classes = [("math", 30, False), ("art", 10, True)]
    classes.append(("bio", 25, False))
    rooms = [("r1", 40, False), ("r2", 12, True)]
    rooms.append(("r3", 26, False))
    plan, utilisation = assign_exam_rooms(classes, rooms)
    assert plan == {"math": "r1", "bio": "r3", "art": "r2"}
    assert utilisation == 0.833
'''
    },
    "P0790": {
        "domain": "Data Aggregation and Statistics",
        "task": "Change points where the windowed mean jumps clearly above local noise",
        "category": "All three target issues",
        "code": '''def change_points(values, window=3, min_jump=5.0, min_gap=2):
    points = []
    for i in range(window, len(values) - window + 1):
        jump = (sum(values[i:i + window]) - sum(values[i - window:i])) / window
        noise = 0.0
        for k in range(i - window, i + window - 1):
            noise += abs(values[k + 1] - values[k])
        noise /= 2 * window - 1
        if abs(jump) >= min_jump and abs(jump) > noise and (not points or i - points[-1][0] >= min_gap):
            points.append((i, round(jump, 2)))
    return points

if __name__ == "__main__":
    series = [1, 1, 1, 10, 10, 10, 10, 10]
    assert change_points(series) == [(3, 9.0)]
    assert change_points([5, 5, 5, 5, 5, 5]) == []
'''
    },
    "P0791": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Cascade of water tanks draining into each other, with overflow losses",
        "category": "All three target issues",
        "code": '''def tank_levels(levels, inflows, outflow_rate, capacity, steps):
    tanks = list(levels)
    overflow = 0.0
    for _ in range(steps):
        for i in range(len(tanks)):
            incoming = inflows[i] + (tanks[i - 1] * outflow_rate if i > 0 else 0.0)
            tanks[i] = tanks[i] + incoming - tanks[i] * outflow_rate
            if tanks[i] > capacity and i == len(tanks) - 1 or tanks[i] > capacity * 1.5:
                overflow += tanks[i] - capacity
                tanks[i] = capacity
    return [round(t, 2) for t in tanks], round(overflow, 2)

if __name__ == "__main__":
    assert tank_levels([0, 0], [10, 0], 0.5, 100, 1) == ([10.0, 5.0], 0.0)
    assert tank_levels([0, 98], [0, 5], 0.0, 100, 1) == ([0.0, 100], 3.0)
'''
    },
    "P0792": {
        "domain": "Matrix & Grid Operations",
        "task": "Sizes of same-value connected regions and the share of cells they cover",
        "category": "All three target issues",
        "code": '''def region_sizes(grid, min_size=2):
    rows, cols = len(grid), len(grid[0])
    seen = set()
    sizes = []
    for r in range(rows):
        for c in range(cols):
            if (r, c) in seen:
                continue
            value = grid[r][c]
            stack = [(r, c)]
            seen.add((r, c))
            size = 0
            while stack:
                cr, cc = stack.pop()
                size += 1
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in seen and grid[nr][nc] == value:
                        seen.add((nr, nc))
                        stack.append((nr, nc))
            if size >= min_size:
                sizes.append((value, size))
    ordered = sorted(sizes, key=lambda s: (-s[1], str(s[0])))
    covered_percent = sum(size for _, size in sizes) * 100 / (rows * cols)
    return ordered, round(covered_percent, 1)

if __name__ == "__main__":
    grid = ["aab", "abb", "ccb"]
    ordered, covered = region_sizes(grid)
    assert ordered == [("b", 4), ("a", 3), ("c", 2)]
    assert covered == 100.0
'''
    },
    "P0793": {
        "domain": "Graph or Tree Traversal",
        "task": "Prim spanning tree that skips forbidden or overweight edges",
        "category": "All three target issues",
        "code": '''import heapq

def constrained_mst(graph, start, forbidden, max_weight):
    visited = {start}
    heap = [(w, start, v) for v, w in graph[start]]
    heapq.heapify(heap)
    edges = []
    while heap and len(visited) < len(graph):
        w, u, v = heapq.heappop(heap)
        if v in visited or (u, v) in forbidden or (v, u) in forbidden or w > max_weight:
            continue
        visited.add(v)
        edges.append((u, v, w))
        for nxt, nw in graph[v]:
            if nxt not in visited:
                heapq.heappush(heap, (nw, v, nxt))
    mean_weight = sum(w for _, _, w in edges) / max(len(edges), 1)
    complete = len(visited) == len(graph)
    return edges, round(mean_weight, 2), complete

if __name__ == "__main__":
    graph = {"a": [("b", 1), ("c", 4)]}
    graph["b"] = [("a", 1), ("c", 2)]
    graph["c"] = [("a", 4), ("b", 2)]
    edges, mean, done = constrained_mst(graph, "a", set(), 10)
    assert (edges, mean, done) == ([("a", "b", 1), ("b", "c", 2)], 1.5, True)
    assert constrained_mst(graph, "a", {("b", "c")}, 10)[1] == 2.5
    assert constrained_mst(graph, "a", set(), 1)[2] is False
'''
    },
    "P0794": {
        "domain": "Searching and Sorting",
        "task": "Intervals overlapping each query range and the covered fraction of the query",
        "category": "All three target issues",
        "code": '''from bisect import bisect_right

def interval_hits(intervals, queries):
    starts = [s for s, _ in intervals]
    results = {}
    for q_start, q_end in queries:
        hits = []
        i = bisect_right(starts, q_end) - 1
        while i >= 0 and len(hits) < 10:
            s, e = intervals[i]
            if e >= q_start and s <= q_end and e - s > 0:
                hits.append((s, e))
            i -= 1
        coverage = sum(min(e, q_end) - max(s, q_start) for s, e in hits) / (q_end - q_start)
        results[q_start, q_end] = sorted(hits), round(coverage, 3)
    return results

if __name__ == "__main__":
    intervals = [(1, 3), (2, 6), (8, 10)]
    results = interval_hits(intervals, [(4, 9), (0, 1)])
    assert results[(4, 9)] == ([(2, 6), (8, 10)], 0.6)
    assert results[(0, 1)] == ([(1, 3)], 0.0)
'''
    },

    # 8. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0795 - P0800)
    "P0795": {
        "domain": "Numerical Computation",
        "task": "Perfect powers up to a limit with base and exponent, optionally odd exponents",
        "category": "Nested loop and complex conditional",
        "code": '''def perfect_powers(limit: int, odd_only: bool = False) -> dict:
    found = {}
    base = 2
    while base * base <= limit:
        value = base * base
        exponent = 2
        while value <= limit:
            if value not in found and (not odd_only or exponent % 2 == 1):
                found[value] = (base, exponent)
            value *= base
            exponent += 1
        base += 1
    return dict(sorted(found.items()))


if __name__ == "__main__":
    powers = perfect_powers(30)
    assert list(powers) == [4, 8, 9, 16, 25, 27]
    assert powers[16] == (2, 4)
    assert perfect_powers(30, True) == {8: (2, 3), 27: (3, 3)}
'''
    },
    "P0796": {
        "domain": "String Processing & Text Analysis",
        "task": "Distinct palindromic substrings of a minimum length, longest first",
        "category": "Nested loop and complex conditional",
        "code": '''def palindromes_in(text, min_len=3):
    s = text.lower()
    found = set()
    for centre in range(len(s)):
        for offset in (0, 1):
            lo, hi = centre, centre + offset
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                if hi - lo + 1 >= min_len:
                    found.add(s[lo:hi + 1])
                lo -= 1
                hi += 1
    return sorted(found, key=lambda p: (-len(p), p))

if __name__ == "__main__":
    found = palindromes_in("Abba racecar")
    assert found == ["racecar", "aceca", "abba", "cec"]
'''
    },
    "P0797": {
        "domain": "Searching and Sorting",
        "task": "Positions in each row that sit at least some depth below both neighbours",
        "category": "Nested loop and complex conditional",
        "code": '''def row_valleys(rows, depth=1):
    valleys = []
    for r, row in enumerate(rows):
        for i in range(1, len(row) - 1):
            if row[i] + depth <= row[i - 1] and row[i] + depth <= row[i + 1] and row[i] >= 0:
                valleys.append((r, i))
    return valleys

if __name__ == "__main__":
    rows = [[5, 1, 5, 2, 3], [0, 0, 0]]
    assert row_valleys(rows) == [(0, 1), (0, 3)]
    assert row_valleys(rows, 3) == [(0, 1)]
'''
    },
    "P0798": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Pairs of equal-length tuples that agree in enough positions",
        "category": "Nested loop and complex conditional",
        "code": '''def aligned_matches(rows, min_shared=2):
    matches = []
    for i in range(len(rows)):
        for j in range(i + 1, len(rows)):
            shared = sum(1 for a, b in zip(rows[i], rows[j]) if a == b)
            if shared >= min_shared and len(rows[i]) == len(rows[j]) and rows[i] != rows[j]:
                matches.append((i, j, shared))
    return matches

if __name__ == "__main__":
    rows = [(1, 2, 3), (1, 2, 4), (1, 2, 3), (9, 9)]
    assert aligned_matches(rows) == [(0, 1, 2), (1, 2, 2)]
'''
    },
    "P0799": {
        "domain": "Graph or Tree Traversal",
        "task": "Find a node on a directed cycle using iterative three-colour DFS",
        "category": "Nested loop and complex conditional",
        "code": '''def find_cycle_node(graph: dict):
    state = {node: 0 for node in graph}
    for root in graph:
        if state[root]:
            continue
        stack = [(root, iter(graph[root]))]
        state[root] = 1
        while stack:
            node, children = stack[-1]
            nxt = next(children, None)
            if nxt is None:
                state[node] = 2
                stack.pop()
            elif nxt in state and state[nxt] == 1 or nxt == node:
                return nxt
            elif nxt in state and state[nxt] == 0:
                state[nxt] = 1
                stack.append((nxt, iter(graph[nxt])))
    return None


if __name__ == "__main__":
    assert find_cycle_node({"a": ["b"], "b": ["c"], "c": ["a"]}) == "a"
    assert find_cycle_node({"a": ["b"], "b": []}) is None
    assert find_cycle_node({"x": ["x"]}) == "x"
'''
    },
    "P0800": {
        "domain": "Inventory and Record Management",
        "task": "Match purchase orders to invoices within amount and date tolerances",
        "category": "Nested loop and complex conditional",
        "code": '''def match_invoices(orders, invoices, amount_tol=0.01, day_tol=5):
    matched = []
    used = set()
    for po_id, po_amount, po_day in orders:
        for inv_id, inv_amount, inv_day in invoices:
            if inv_id not in used and abs(inv_amount - po_amount) <= amount_tol * po_amount and abs(inv_day - po_day) <= day_tol:
                used.add(inv_id)
                matched.append((po_id, inv_id))
                break
    return matched, [i for i, _, _ in invoices if i not in used]

if __name__ == "__main__":
    orders = [("po1", 100.0, 1), ("po2", 50.0, 10)]
    invoices = [("i1", 50.2, 12), ("i2", 100.5, 3)]
    invoices.append(("i3", 70.0, 1))
    matched, unmatched = match_invoices(orders, invoices)
    assert matched == [("po1", "i2"), ("po2", "i1")]
    assert unmatched == ["i3"]
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 16",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v16.0-expansion",
        "programs": BATCH16_PROGRAMS,
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


def check_architecture_fit(pid, row, code, allow_scaffold_issues=False):
    """
    Reasons a new program would not work in the refactoring pipeline:
    - unknown domain or intended_category;
    - the labels generate_dataset.py assigns differ from intended_category;
    - a target issue sits in the __main__ test block rather than program
      logic (allowed for batches 1-10 via allow_scaffold_issues);
    - two records start on the same line (main.py keys actions by line);
    - it uses a name that transformation.py introduces;
    - it has no assert-based self-test under __main__, or that test fails.
    """
    # Imported here: generate_dataset imports this module via validate_corpus.
    from generate_dataset import extract_statements

    problems = []
    domain, category = row["domain"], row["intended_category"]

    if domain not in DOMAINS:
        problems.append(f"{pid} has unknown domain {domain!r}")

    if category not in CATEGORY_LABELS:
        problems.append(f"{pid} has unknown category {category!r}")

    tree = ast.parse(code)
    records = extract_statements(tree, code.splitlines(keepends=True))

    labels = {
        label
        for record in records
        for label in ("long_statement", "nested_loop", "complex_conditional")
        if record[label]
    }
    expected = CATEGORY_LABELS.get(category)
    if expected is not None and labels != expected:
        problems.append(
            f"{pid} is {category!r} but its rule labels are "
            f"{sorted(labels) or 'none'}"
        )

    if not allow_scaffold_issues:
        scaffold = sorted({
            record["line_no"]
            for record in records
            if record["in_main_guard"] and any(
                record[label]
                for label in ("long_statement", "nested_loop",
                              "complex_conditional")
            )
        })
        if scaffold:
            problems.append(
                f"{pid} has target issues in its __main__ block on "
                f"line(s) {scaffold}"
            )

    starts = [record["line_no"] for record in records]
    shared = sorted({line for line in starts if starts.count(line) > 1})
    if shared:
        problems.append(f"{pid} has several statements on line(s) {shared}")

    reserved = RESERVED_NAMES & {
        node.id for node in ast.walk(tree) if isinstance(node, ast.Name)
    }
    if reserved:
        problems.append(f"{pid} uses reserved name(s) {sorted(reserved)}")

    has_self_test = any(
        isinstance(node, ast.If)
        and "__main__" in ast.unparse(node.test)
        and any(isinstance(n, ast.Assert) for n in ast.walk(node))
        for node in tree.body
    )
    if not has_self_test:
        problems.append(f"{pid} has no assert-based __main__ self-test")
    else:
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(code, f"{pid}.py", "exec"), {"__name__": "__main__"})
        except Exception as error:
            problems.append(
                f"{pid} self-test failed: {type(error).__name__}: {error}"
            )

    return problems


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

    fit_problems = [
        problem
        for pid, filepath, code, row in planned
        if not filepath.exists()
        for problem in check_architecture_fit(pid, row, code)
    ]

    if fit_problems:
        raise SystemExit(
            "Nothing was written. These new programs do not fit the "
            "pipeline:\n- " + "\n- ".join(fit_problems)
        )

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