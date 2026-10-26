"""
build_corpus.py
Writes the Batch 10 (P0451-P0500) programs into program_corpus/programs and
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

BATCH10_PROGRAMS = {
    # 1. NONE (8 programs: P0451 - P0458)
    "P0451": {
        "domain": "Numerical Computation",
        "task": "Count trailing zeros of n factorial using powers of five",
        "category": "None",
        "code": '''def factorial_trailing_zeros(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    zeros = 0
    power_of_five = 5
    while power_of_five <= n:
        zeros += n // power_of_five
        power_of_five *= 5
    return zeros

if __name__ == "__main__":
    assert factorial_trailing_zeros(100) == 24
    assert factorial_trailing_zeros(4) == 0
'''
    },
    "P0452": {
        "domain": "String Processing & Text Analysis",
        "task": "Letters missing from a sentence for it to be a pangram",
        "category": "None",
        "code": '''import string

def missing_pangram_letters(text: str) -> str:
    present = set(text.lower())
    alphabet = set(string.ascii_lowercase)
    return "".join(sorted(alphabet - present))

if __name__ == "__main__":
    sentence = "The quick brown fox jumps over the lazy dog"
    assert missing_pangram_letters(sentence) == ""
    assert missing_pangram_letters("abc") == string.ascii_lowercase[3:]
'''
    },
    "P0453": {
        "domain": "Searching and Sorting",
        "task": "First and last index of a value in a sorted list via bisection",
        "category": "None",
        "code": '''import bisect

def first_last_positions(items: list[int], target: int) -> tuple[int, int]:
    left = bisect.bisect_left(items, target)
    if left == len(items) or items[left] != target:
        return -1, -1
    right = bisect.bisect_right(items, target) - 1
    return left, right

if __name__ == "__main__":
    assert first_last_positions([1, 2, 2, 2, 5], 2) == (1, 3)
    assert first_last_positions([1, 2, 2, 2, 5], 3) == (-1, -1)
'''
    },
    "P0454": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Top k most frequent items with alphabetical tie breaking",
        "category": "None",
        "code": '''from collections import Counter

def top_k_frequent(items: list[str], k: int) -> list[str]:
    counts = Counter(items)
    ranked = sorted(counts, key=lambda w: (-counts[w], w))
    return ranked[:k]

if __name__ == "__main__":
    words = ["b", "a", "c", "b", "a", "d"]
    assert top_k_frequent(words, 2) == ["a", "b"]
'''
    },
    "P0455": {
        "domain": "Graph or Tree Traversal",
        "task": "Maximum depth of a rooted tree by recursion over child lists",
        "category": "None",
        "code": '''def tree_max_depth(children: dict[str, list[str]], node: str) -> int:
    kids = children.get(node, [])
    if not kids:
        return 1
    depths = [tree_max_depth(children, kid) for kid in kids]
    return 1 + max(depths)

if __name__ == "__main__":
    tree = {"a": ["b", "c"], "b": ["d"]}
    assert tree_max_depth(tree, "a") == 3
    assert tree_max_depth({}, "x") == 1
'''
    },
    "P0456": {
        "domain": "Scheduling and Resource Allocation",
        "task": "First free gap of a given length in a day calendar",
        "category": "None",
        "code": '''def first_free_gap(busy: list[tuple[int, int]], day_start: int, day_end: int, length: int) -> int:
    cursor = day_start
    for start, end in sorted(busy):
        if start - cursor >= length:
            return cursor
        cursor = max(cursor, end)
    return cursor if day_end - cursor >= length else -1

if __name__ == "__main__":
    busy = [(9, 10), (10, 12), (13, 14)]
    assert first_free_gap(busy, 9, 17, 1) == 12
    assert first_free_gap(busy, 9, 17, 2) == 14
    assert first_free_gap(busy, 9, 17, 4) == -1
'''
    },
    "P0457": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Traffic light colour at a given second of a fixed phase cycle",
        "category": "None",
        "code": '''PHASES = (("green", 30), ("yellow", 5), ("red", 25))

def light_at_time(seconds: int) -> str:
    cycle = sum(duration for _, duration in PHASES)
    offset = seconds % cycle
    for colour, duration in PHASES:
        if offset < duration:
            return colour
        offset -= duration
    return "red"

if __name__ == "__main__":
    assert light_at_time(0) == "green"
    assert light_at_time(32) == "yellow"
    assert light_at_time(59) == "red"
    assert light_at_time(60) == "green"
'''
    },
    "P0458": {
        "domain": "Inventory and Record Management",
        "task": "Parse a warehouse bin location code into aisle, rack and level",
        "category": "None",
        "code": '''def parse_bin_location(code: str) -> tuple[str, int, int]:
    parts = code.upper().split("-")
    if len(parts) != 3:
        raise ValueError("expected AISLE-RACK-LEVEL")
    aisle, rack, level = parts
    return aisle, int(rack), int(level)

if __name__ == "__main__":
    assert parse_bin_location("a-12-3") == ("A", 12, 3)
'''
    },

    # 2. LONG STATEMENT ONLY (6 programs: P0459 - P0464)
    "P0459": {
        "domain": "Numerical Computation",
        "task": "Lorentz factor and relativistic to classical kinetic energy ratio",
        "category": "Long statement only",
        "code": '''import math

def relativistic_energy(mass_kg: float, speed_fraction_c: float) -> tuple[float, float]:
    c = 299_792_458.0
    lorentz_factor = 1.0 / math.sqrt(1.0 - speed_fraction_c ** 2)
    kinetic_energy_j = (lorentz_factor - 1.0) * mass_kg * c ** 2
    classical_ratio = kinetic_energy_j / (0.5 * mass_kg * (speed_fraction_c * c) ** 2)
    return round(lorentz_factor, 4), round(classical_ratio, 4)

if __name__ == "__main__":
    assert relativistic_energy(1.0, 0.6) == (1.25, 1.3889)
'''
    },
    "P0460": {
        "domain": "Data Aggregation and Statistics",
        "task": "Survey sample size for a proportion with finite population correction",
        "category": "Long statement only",
        "code": '''import math

def survey_sample_size(proportion: float, margin: float, population: int, z: float = 1.96) -> int:
    infinite_size = (z ** 2) * proportion * (1.0 - proportion) / (margin ** 2)
    adjusted_size = infinite_size / (1.0 + (infinite_size - 1.0) / population)
    return math.ceil(adjusted_size)

if __name__ == "__main__":
    assert survey_sample_size(0.5, 0.05, 10 ** 9) == 385
    assert survey_sample_size(0.5, 0.05, 1000) == 278
'''
    },
    "P0461": {
        "domain": "String Processing & Text Analysis",
        "task": "Cosine similarity of character trigram profiles of two strings",
        "category": "Long statement only",
        "code": '''import math
from collections import Counter

def trigram_cosine(a: str, b: str) -> float:
    grams_a = Counter(a.lower()[i:i + 3] for i in range(len(a) - 2))
    grams_b = Counter(b.lower()[i:i + 3] for i in range(len(b) - 2))
    dot = sum(grams_a[g] * grams_b[g] for g in grams_a)
    norm = math.sqrt(sum(v * v for v in grams_a.values())) * math.sqrt(sum(v * v for v in grams_b.values()))
    return round(dot / norm, 4) if norm else 0.0

if __name__ == "__main__":
    assert trigram_cosine("night", "night") == 1.0
    assert trigram_cosine("ab", "cd") == 0.0
'''
    },
    "P0462": {
        "domain": "Inventory and Record Management",
        "task": "Days of supply and projected shortfall over a replenishment lead time",
        "category": "Long statement only",
        "code": '''def stockout_projection(on_hand: int, daily_demand: float, lead_time_days: int, pending_receipt: int) -> tuple[float, int]:
    days_of_supply = (on_hand + pending_receipt) / daily_demand if daily_demand > 0 else float("inf")
    shortfall_units = max(0, round(daily_demand * lead_time_days - on_hand - pending_receipt))
    return round(days_of_supply, 1), shortfall_units

if __name__ == "__main__":
    assert stockout_projection(100, 20.0, 7, 20) == (6.0, 20)
'''
    },
    "P0463": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Sprint capacity in story points from team availability and focus factor",
        "category": "Long statement only",
        "code": '''def sprint_capacity_points(leave_by_member: dict[str, int], sprint_days: int, focus_factor: float, velocity_per_day: float) -> tuple[float, str]:
    person_days = [max(0, sprint_days - leave) for leave in leave_by_member.values()]
    capacity_points = sum(person_days) * focus_factor * velocity_per_day
    least_available = min(leave_by_member, key=lambda name: -leave_by_member[name])
    return round(capacity_points, 1), least_available

if __name__ == "__main__":
    leave = {"ana": 0, "raj": 3, "li": 1}
    assert sprint_capacity_points(leave, 10, 0.7, 1.5) == (27.3, "raj")
'''
    },
    "P0464": {
        "domain": "Matrix & Grid Operations",
        "task": "Rotate and uniformly scale a 2D point about the origin",
        "category": "Long statement only",
        "code": '''import math

def rotate_scale_point(x: float, y: float, angle_deg: float, scale: float) -> tuple[float, float]:
    theta = math.radians(angle_deg)
    rotated_x = scale * (x * math.cos(theta) - y * math.sin(theta))
    rotated_y = scale * (x * math.sin(theta) + y * math.cos(theta))
    return round(rotated_x, 6), round(rotated_y, 6)

if __name__ == "__main__":
    assert rotate_scale_point(1.0, 0.0, 90.0, 2.0) == (0.0, 2.0)
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0465 - P0470)
    "P0465": {
        "domain": "Matrix & Grid Operations",
        "task": "Boolean matrix product of two 0/1 adjacency matrices",
        "category": "Nested loop only",
        "code": '''def boolean_matrix_product(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    size = len(b[0])
    result = []
    for row in a:
        out_row = []
        for j in range(size):
            column = [b_row[j] for b_row in b]
            hit = any(x and y for x, y in zip(row, column))
            out_row.append(int(hit))
        result.append(out_row)
    return result

if __name__ == "__main__":
    left = [[1, 0], [0, 1]]
    right = [[0, 1], [1, 0]]
    assert boolean_matrix_product(left, right) == [[0, 1], [1, 0]]
'''
    },
    "P0466": {
        "domain": "Searching and Sorting",
        "task": "Cycle sort that also counts memory writes",
        "category": "Nested loop only",
        "code": '''def cycle_sort_writes(values: list[int]) -> tuple[list[int], int]:
    data = list(values)
    writes = 0
    for start in range(len(data) - 1):
        item = data[start]
        pos = start
        for i in range(start + 1, len(data)):
            if data[i] < item:
                pos += 1
        if pos == start:
            continue
        while item == data[pos]:
            pos += 1
        data[pos], item = item, data[pos]
        writes += 1
        while pos != start:
            pos = start
            for i in range(start + 1, len(data)):
                if data[i] < item:
                    pos += 1
            while item == data[pos]:
                pos += 1
            data[pos], item = item, data[pos]
            writes += 1
    return data, writes

if __name__ == "__main__":
    assert cycle_sort_writes([5, 2, 4, 2, 1])[0] == [1, 2, 2, 4, 5]
    assert cycle_sort_writes([1, 2, 3]) == ([1, 2, 3], 0)
'''
    },
    "P0467": {
        "domain": "Graph or Tree Traversal",
        "task": "Count simple paths between two nodes of a directed graph",
        "category": "Nested loop only",
        "code": '''def count_simple_paths(graph: dict[str, list[str]], src: str, dst: str) -> int:
    total = 0
    stack = [(src, [src])]
    while stack:
        node, path = stack.pop()
        if node == dst:
            total += 1
            continue
        for nxt in graph.get(node, []):
            if nxt not in path:
                stack.append((nxt, path + [nxt]))
    return total

if __name__ == "__main__":
    graph = {"a": ["b", "c"], "b": ["c", "d"], "c": ["d"]}
    assert count_simple_paths(graph, "a", "d") == 3
'''
    },
    "P0468": {
        "domain": "String Processing & Text Analysis",
        "task": "Pad table cells so columns line up in plain text",
        "category": "Nested loop only",
        "code": '''def align_columns(rows: list[list[str]]) -> list[str]:
    widths = [0] * max(len(row) for row in rows)
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))
    lines = []
    for row in rows:
        padded = [c.ljust(widths[i]) for i, c in enumerate(row)]
        lines.append(" | ".join(padded).rstrip())
    return lines

if __name__ == "__main__":
    table = [["id", "name"], ["7", "Ann"]]
    assert align_columns(table) == ["id | name", "7  | Ann"]
'''
    },
    "P0469": {
        "domain": "Data Aggregation and Statistics",
        "task": "Histogram counts of values over half-open bin edges",
        "category": "Nested loop only",
        "code": '''def histogram_counts(values: list[float], edges: list[float]) -> list[int]:
    counts = [0] * (len(edges) - 1)
    for value in values:
        for i in range(len(edges) - 1):
            if edges[i] <= value < edges[i + 1]:
                counts[i] += 1
                break
    return counts

if __name__ == "__main__":
    data = [1.0, 2.0, 2.5, 9.0, 10.0]
    assert histogram_counts(data, [0.0, 2.0, 5.0, 10.0]) == [1, 2, 1]
'''
    },
    "P0470": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Bank tellers serving a queue, each customer going to the earliest free teller",
        "category": "Nested loop only",
        "code": '''def teller_finish_times(service_times: list[int], tellers: int) -> list[int]:
    free_at = [0] * tellers
    finishes = []
    for duration in service_times:
        best = 0
        for t in range(1, tellers):
            if free_at[t] < free_at[best]:
                best = t
        free_at[best] += duration
        finishes.append(free_at[best])
    return finishes

if __name__ == "__main__":
    assert teller_finish_times([5, 3, 2, 4], 2) == [5, 3, 5, 9]
'''
    },

    # 4. COMPLEX CONDITIONAL ONLY (6 programs: P0471 - P0476)
    "P0471": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate a 24-hour clock time written as HH:MM or HH:MM:SS",
        "category": "Complex conditional only",
        "code": '''def is_valid_clock_time(text: str) -> bool:
    parts = text.split(":")
    if len(parts) not in (2, 3) or not all(p.isdigit() and len(p) == 2 for p in parts):
        return False
    hours, minutes = int(parts[0]), int(parts[1])
    seconds = int(parts[2]) if len(parts) == 3 else 0
    if hours > 23 or minutes > 59 or seconds > 59:
        return False
    return True

if __name__ == "__main__":
    assert is_valid_clock_time("23:59") is True
    assert is_valid_clock_time("24:00") is False
    assert is_valid_clock_time("7:00") is False
    assert is_valid_clock_time("12:30:60") is False
'''
    },
    "P0472": {
        "domain": "Inventory and Record Management",
        "task": "Restocking fee rate for a customer return by age, receipt and category",
        "category": "Complex conditional only",
        "code": '''def return_restock_fee(days_since_purchase: int, opened: bool, category: str, has_receipt: bool) -> float:
    if days_since_purchase > 30 or not has_receipt:
        return -1.0
    if opened and category in {"electronics", "software"} and days_since_purchase > 14:
        return 0.15
    return 0.0

if __name__ == "__main__":
    assert return_restock_fee(40, False, "toys", True) == -1.0
    assert return_restock_fee(20, True, "electronics", True) == 0.15
    assert return_restock_fee(5, True, "electronics", True) == 0.0
'''
    },
    "P0473": {
        "domain": "Graph or Tree Traversal",
        "task": "Check the binary search tree property with recursive value bounds",
        "category": "Complex conditional only",
        "code": '''def is_valid_bst(tree: dict[int, tuple[int | None, int | None]], node: int | None, low: float = float("-inf"), high: float = float("inf")) -> bool:
    if node is None:
        return True
    if node <= low or node >= high or node not in tree:
        return False
    left, right = tree[node]
    left_ok = is_valid_bst(tree, left, low, node)
    return left_ok and is_valid_bst(tree, right, node, high)

if __name__ == "__main__":
    tree = {5: (3, 8), 3: (None, None), 8: (None, None)}
    assert is_valid_bst(tree, 5) is True
    bad = dict(tree)
    bad[3] = (None, 6)
    bad[6] = (None, None)
    assert is_valid_bst(bad, 5) is False
'''
    },
    "P0474": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Approve a shift swap between two workers under role and hour limits",
        "category": "Complex conditional only",
        "code": '''def can_swap_shifts(worker_a: dict, worker_b: dict, shift_hours: int) -> bool:
    same_role = worker_a["role"] == worker_b["role"]
    a_hours = worker_a["week_hours"]
    b_hours = worker_b["week_hours"]
    if not same_role or a_hours + shift_hours > 48 or b_hours + shift_hours > 48:
        return False
    return worker_a["certified"] and worker_b["certified"]

if __name__ == "__main__":
    a = dict(role="rn", week_hours=40, certified=True)
    b = dict(role="rn", week_hours=36, certified=True)
    assert can_swap_shifts(a, b, 8) is True
    assert can_swap_shifts(a, b, 12) is False
'''
    },
    "P0475": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Chess castling legality from move history, path and attacked squares",
        "category": "Complex conditional only",
        "code": '''def can_castle(king_moved: bool, rook_moved: bool, path: list[tuple[str, str]], attacked: set[str], in_check: bool) -> bool:
    path_clear = all(piece == "." for _, piece in path)
    if king_moved or rook_moved or in_check or not path_clear:
        return False
    king_squares = [name for name, _ in path[:2]]
    return not any(name in attacked for name in king_squares)

if __name__ == "__main__":
    path = [("f1", "."), ("g1", ".")]
    assert can_castle(False, False, path, set(), False) is True
    assert can_castle(False, False, path, {"f1"}, False) is False
    assert can_castle(False, False, [("f1", "N")], set(), False) is False
'''
    },
    "P0476": {
        "domain": "Data Aggregation and Statistics",
        "task": "Screen a sample for normality using skewness and kurtosis z-scores",
        "category": "Complex conditional only",
        "code": '''import math

def passes_normality_screen(skewness: float, excess_kurtosis: float, n: int) -> bool:
    if n < 8:
        return False
    numerator = 6.0 * n * (n - 1)
    denominator = (n - 2) * (n + 1) * (n + 3)
    se_skew = math.sqrt(numerator / denominator)
    ratio = (n * n - 1) / ((n - 3) * (n + 5))
    se_kurt = 2.0 * se_skew * math.sqrt(ratio)
    z_skew = skewness / se_skew
    z_kurt = excess_kurtosis / se_kurt
    if abs(z_skew) <= 1.96 and abs(z_kurt) <= 1.96 and n <= 5000:
        return True
    return False

if __name__ == "__main__":
    assert passes_normality_screen(0.1, 0.2, 100) is True
    assert passes_normality_screen(2.0, 0.0, 100) is False
    assert passes_normality_screen(0.0, 0.0, 5) is False
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (6 programs: P0477 - P0482)
    "P0477": {
        "domain": "Matrix & Grid Operations",
        "task": "Matrix exponential by truncated Taylor series",
        "category": "Long statement and nested loop",
        "code": '''def matrix_exponential_taylor(matrix: list[list[float]], terms: int = 12) -> list[list[float]]:
    size = len(matrix)
    result = [[float(i == j) for j in range(size)] for i in range(size)]
    term = [row[:] for row in result]
    for k in range(1, terms):
        term = [[sum(term[i][m] * matrix[m][j] for m in range(size)) / k for j in range(size)] for i in range(size)]
        for i in range(size):
            for j in range(size):
                result[i][j] += term[i][j]
    return [[round(v, 4) for v in row] for row in result]

if __name__ == "__main__":
    assert matrix_exponential_taylor([[0.0, 0.0], [0.0, 0.0]]) == [[1.0, 0.0], [0.0, 1.0]]
    assert matrix_exponential_taylor([[1.0, 0.0], [0.0, 0.0]]) == [[2.7183, 0.0], [0.0, 1.0]]
'''
    },
    "P0478": {
        "domain": "Data Aggregation and Statistics",
        "task": "Gaussian kernel density estimate evaluated on a grid of points",
        "category": "Long statement and nested loop",
        "code": '''import math

def gaussian_kde(samples: list[float], grid: list[float], bandwidth: float) -> list[float]:
    n = len(samples)
    densities = []
    for x in grid:
        total = 0.0
        for s in samples:
            total += math.exp(-0.5 * ((x - s) / bandwidth) ** 2) / (bandwidth * math.sqrt(2.0 * math.pi))
        densities.append(round(total / n, 4))
    return densities

if __name__ == "__main__":
    assert gaussian_kde([0.0], [0.0], 1.0) == [0.3989]
'''
    },
    "P0479": {
        "domain": "Inventory and Record Management",
        "task": "Explode a multi-level bill of materials into total component quantities",
        "category": "Long statement and nested loop",
        "code": '''def explode_bill_of_materials(bom: dict[str, list[tuple[str, int]]], product: str, quantity: int) -> dict[str, int]:
    totals: dict[str, int] = {}
    frontier = [(product, quantity)]
    while frontier:
        item, qty = frontier.pop()
        for component, per_unit in bom.get(item, []):
            totals[component] = totals.get(component, 0) + qty * per_unit
            frontier.append((component, qty * per_unit))
    return totals

if __name__ == "__main__":
    bom = {"bike": [("wheel", 2), ("frame", 1)]}
    bom["wheel"] = [("spoke", 32)]
    expected = {"wheel": 6, "frame": 3, "spoke": 192}
    assert explode_bill_of_materials(bom, "bike", 3) == expected
'''
    },
    "P0480": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Johnson's rule order and makespan for a two-machine flow shop",
        "category": "Long statement and nested loop",
        "code": '''def johnson_rule_schedule(jobs: dict[str, tuple[int, int]]) -> tuple[list[str], int]:
    first_group = sorted((name for name, (a, b) in jobs.items() if a <= b), key=lambda name: jobs[name][0])
    second_group = sorted((name for name, (a, b) in jobs.items() if a > b), key=lambda name: -jobs[name][1])
    order = first_group + second_group
    finish = [0, 0]
    for name in order:
        for machine in range(2):
            ready = finish[machine - 1] if machine else 0
            finish[machine] = max(finish[machine], ready) + jobs[name][machine]
    return order, finish[1]

if __name__ == "__main__":
    jobs = {"A": (3, 6), "B": (5, 2), "C": (1, 2)}
    assert johnson_rule_schedule(jobs) == (["C", "A", "B"], 12)
'''
    },
    "P0481": {
        "domain": "String Processing & Text Analysis",
        "task": "Smith-Waterman local alignment score of two sequences",
        "category": "Long statement and nested loop",
        "code": '''def local_alignment_score(a: str, b: str, match: int = 2, mismatch: int = -1, gap: int = -2) -> int:
    rows, cols = len(a) + 1, len(b) + 1
    score = [[0] * cols for _ in range(rows)]
    best = 0
    for i in range(1, rows):
        for j in range(1, cols):
            diagonal = score[i - 1][j - 1] + (match if a[i - 1] == b[j - 1] else mismatch)
            score[i][j] = max(0, diagonal, score[i - 1][j] + gap, score[i][j - 1] + gap)
            best = max(best, score[i][j])
    return best

if __name__ == "__main__":
    assert local_alignment_score("abc", "abc") == 6
    assert local_alignment_score("xabcx", "yabcy") == 6
'''
    },
    "P0482": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "DeGroot opinion averaging over a trust network for several rounds",
        "category": "Long statement and nested loop",
        "code": '''def degroot_consensus(opinions: list[float], trust: list[list[float]], rounds: int) -> list[float]:
    current = list(opinions)
    for _ in range(rounds):
        updated = []
        for weights in trust:
            updated.append(sum(w * o for w, o in zip(weights, current)) / max(sum(weights), 1e-9))
        current = updated
    return [round(value, 4) for value in current]

if __name__ == "__main__":
    trust = [[0.5, 0.5], [0.5, 0.5]]
    assert degroot_consensus([0.0, 1.0], trust, 1) == [0.5, 0.5]
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0483 - P0488)
    "P0483": {
        "domain": "Numerical Computation",
        "task": "Midspan deflection of a simply supported beam against a span ratio limit",
        "category": "Long statement and complex conditional",
        "code": '''def beam_deflection_ok(load_n: float, span_m: float, modulus_pa: float, inertia_m4: float, deflection_ratio: int = 360) -> tuple[float, bool]:
    if span_m <= 0 or modulus_pa <= 0 or inertia_m4 <= 0:
        raise ValueError("invalid section")
    max_deflection_m = 5.0 * load_n * span_m ** 3 / (384.0 * modulus_pa * inertia_m4)
    allowed_m = span_m / deflection_ratio
    return round(max_deflection_m * 1000.0, 3), max_deflection_m <= allowed_m

if __name__ == "__main__":
    deflection_mm, ok = beam_deflection_ok(10000.0, 4.0, 200e9, 8e-6)
    assert deflection_mm == 5.208 and ok is True
'''
    },
    "P0484": {
        "domain": "Data Aggregation and Statistics",
        "task": "Grubbs test for a single outlier against a critical G value",
        "category": "Long statement and complex conditional",
        "code": '''import statistics

def grubbs_single_outlier(values: list[float], critical_g: float) -> float | None:
    mean = statistics.mean(values)
    sd = statistics.stdev(values)
    suspect = max(values, key=lambda v: abs(v - mean))
    standardized_distance_of_suspect = abs(suspect - mean) / sd if sd > 0 else 0.0
    if len(values) >= 3 and sd > 0 and standardized_distance_of_suspect > critical_g:
        return suspect
    return None

if __name__ == "__main__":
    assert grubbs_single_outlier([1.0, 2.0, 3.0, 2.0, 50.0], 1.715) == 50.0
    assert grubbs_single_outlier([1.0, 2.0, 3.0], 1.15) is None
'''
    },
    "P0485": {
        "domain": "String Processing & Text Analysis",
        "task": "Build a URL slug from a title, trimmed at a word boundary",
        "category": "Long statement and complex conditional",
        "code": '''def slugify(title: str, max_length: int = 40) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in title.lower().strip())
    collapsed = "-".join(part for part in cleaned.split("-") if part)
    if len(collapsed) > max_length and "-" in collapsed[:max_length] and max_length > 0:
        collapsed = collapsed[:max_length].rsplit("-", 1)[0]
    return collapsed

if __name__ == "__main__":
    assert slugify("Hello, World! 2026") == "hello-world-2026"
    assert slugify("Alpha beta gamma", 12) == "alpha-beta"
'''
    },
    "P0486": {
        "domain": "Inventory and Record Management",
        "task": "Warranty claim outcome of replace, repair or reject by depreciated value",
        "category": "Long statement and complex conditional",
        "code": '''def warranty_claim_outcome(purchase_price: float, age_months: int, warranty_months: int, physical_damage: bool, repair_quote: float) -> tuple[str, float]:
    depreciated_value = purchase_price * max(0.0, 1.0 - age_months / (warranty_months * 2.0))
    if age_months <= warranty_months and not physical_damage and repair_quote > 0.6 * depreciated_value:
        return "replace", round(depreciated_value, 2)
    if age_months <= warranty_months and not physical_damage:
        return "repair", round(repair_quote, 2)
    return "reject", 0.0

if __name__ == "__main__":
    assert warranty_claim_outcome(1000.0, 6, 12, False, 800.0) == ("replace", 750.0)
    assert warranty_claim_outcome(1000.0, 6, 12, False, 100.0) == ("repair", 100.0)
    assert warranty_claim_outcome(1000.0, 6, 12, True, 100.0) == ("reject", 0.0)
'''
    },
    "P0487": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Book a computer lab within opening hours and price evening sessions",
        "category": "Long statement and complex conditional",
        "code": '''def can_book_lab(seats_needed: int, lab: dict, start_hour: int, end_hour: int) -> tuple[bool, float]:
    booking_cost = (end_hour - start_hour) * lab["hourly_rate"] * (1.5 if start_hour >= 18 else 1.0)
    if seats_needed <= lab["seats"] and lab["open"] <= start_hour < end_hour <= lab["close"]:
        return True, round(booking_cost, 2)
    return False, 0.0

if __name__ == "__main__":
    lab = dict(seats=30, open=8, close=20, hourly_rate=10.0)
    assert can_book_lab(25, lab, 18, 20) == (True, 30.0)
    assert can_book_lab(25, lab, 19, 21) == (False, 0.0)
'''
    },
    "P0488": {
        "domain": "Graph or Tree Traversal",
        "task": "End-to-end transfer time of a payload along a network path",
        "category": "Long statement and complex conditional",
        "code": '''def path_transfer_time_ms(path: list[str], link_latency_ms: dict[tuple[str, str], float], payload_kb: float, bandwidth_mbps: float) -> float:
    total_ms = 0.0
    for a, b in zip(path, path[1:]):
        latency = link_latency_ms.get((a, b), link_latency_ms.get((b, a)))
        if latency is None or bandwidth_mbps <= 0 or payload_kb < 0:
            return -1.0
        total_ms += latency + payload_kb * 8.0 / bandwidth_mbps
    return round(total_ms, 3)

if __name__ == "__main__":
    links = {("a", "b"): 5.0, ("c", "b"): 10.0}
    assert path_transfer_time_ms(["a", "b", "c"], links, 125.0, 100.0) == 35.0
    assert path_transfer_time_ms(["a", "c"], links, 125.0, 100.0) == -1.0
'''
    },

    # 7. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0489 - P0494)
    "P0489": {
        "domain": "Matrix & Grid Operations",
        "task": "Minesweeper hint numbers for every safe cell of a board",
        "category": "Nested loop and complex conditional",
        "code": '''def minesweeper_hints(board: list[str]) -> list[str]:
    rows, cols = len(board), len(board[0])
    output = []
    for r in range(rows):
        line = ""
        for c in range(cols):
            if board[r][c] == "*":
                line += "*"
                continue
            count = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == "*":
                        count += 1
            line += str(count) if count else "."
        output.append(line)
    return output

if __name__ == "__main__":
    assert minesweeper_hints(["*..", "...", "..*"]) == ["*1.", "121", ".1*"]
'''
    },
    "P0490": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Find likely duplicate contacts by email or phone suffix and initial",
        "category": "Nested loop and complex conditional",
        "code": '''def duplicate_contacts(contacts: list[dict[str, str]]) -> list[tuple[int, int]]:
    pairs = []
    for i in range(len(contacts)):
        for j in range(i + 1, len(contacts)):
            a, b = contacts[i], contacts[j]
            same_email = a["email"].lower() == b["email"].lower()
            same_phone = a["phone"][-7:] == b["phone"][-7:]
            if same_email or (same_phone and a["name"][0] == b["name"][0]):
                pairs.append((i, j))
    return pairs

if __name__ == "__main__":
    c1 = dict(name="Ann", email="A@x.com", phone="5551234567")
    c2 = dict(name="Al", email="al@y.com", phone="15551234567")
    c3 = dict(name="Bob", email="a@X.com", phone="000")
    assert duplicate_contacts([c1, c2, c3]) == [(0, 1), (0, 2)]
'''
    },
    "P0491": {
        "domain": "Graph or Tree Traversal",
        "task": "Find bridge edges by removing each edge and testing connectivity",
        "category": "Nested loop and complex conditional",
        "code": '''def bridge_edges(nodes: list[str], edges: list[tuple[str, str]]) -> list[tuple[str, str]]:
    bridges = []
    for removed in edges:
        remaining = [e for e in edges if e != removed]
        seen = {nodes[0]}
        stack = [nodes[0]]
        while stack:
            node = stack.pop()
            for u, v in remaining:
                other = v if u == node else u
                if node in (u, v) and other not in seen and u != v:
                    seen.add(other)
                    stack.append(other)
        if len(seen) < len(nodes):
            bridges.append(removed)
    return bridges

if __name__ == "__main__":
    edges = [("a", "b"), ("b", "c"), ("c", "a"), ("c", "d")]
    assert bridge_edges(["a", "b", "c", "d"], edges) == [("c", "d")]
'''
    },
    "P0492": {
        "domain": "String Processing & Text Analysis",
        "task": "Locate the expansion of each acronym among consecutive words",
        "category": "Nested loop and complex conditional",
        "code": '''def acronym_expansions(words: list[str], acronyms: list[str]) -> dict[str, str]:
    found = {}
    for acronym in acronyms:
        size = len(acronym)
        for start in range(len(words) - size + 1):
            window = words[start:start + size]
            initials = "".join(w[0].upper() for w in window if w)
            long_words = all(len(w) > 1 for w in window)
            if initials == acronym and acronym not in found and long_words:
                found[acronym] = " ".join(window)
    return found

if __name__ == "__main__":
    words = "the world health organization met".split()
    expected = {"WHO": "world health organization"}
    assert acronym_expansions(words, ["WHO", "XYZ"]) == expected
'''
    },
    "P0493": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Students whose enrolled exams clash in the same timetable slot",
        "category": "Nested loop and complex conditional",
        "code": '''def exam_clash_students(enrolments: dict[str, list[str]], slot_of: dict[str, int]) -> list[str]:
    clashing = []
    for student, exams in enrolments.items():
        seen_slots = set()
        for exam in exams:
            slot = slot_of.get(exam)
            if slot is not None and slot in seen_slots and student not in clashing:
                clashing.append(student)
            seen_slots.add(slot)
    return clashing

if __name__ == "__main__":
    enrolments = {"s1": ["m", "p"], "s2": ["m", "c"]}
    slots = {"m": 1, "p": 1, "c": 2}
    assert exam_clash_students(enrolments, slots) == ["s1"]
'''
    },
    "P0494": {
        "domain": "Inventory and Record Management",
        "task": "First-expiry-first-out pick list skipping lots close to expiry",
        "category": "Nested loop and complex conditional",
        "code": '''def fefo_pick(orders: list[tuple[str, int]], lots: list[tuple[str, str, int, int]], today: int) -> list[tuple[str, str, int]]:
    remaining = {lot[0]: lot[2] for lot in lots}
    picks = []
    for sku, wanted in orders:
        for lot_id, lot_sku, _, expiry in sorted(lots, key=lambda lot: lot[3]):
            take = min(wanted, remaining[lot_id])
            if lot_sku == sku and take > 0 and expiry > today + 2:
                picks.append((sku, lot_id, take))
                remaining[lot_id] -= take
                wanted -= take
    return picks

if __name__ == "__main__":
    lots = [("L1", "A", 5, 10), ("L2", "A", 5, 5)]
    lots.append(("L3", "A", 5, 1))
    assert fefo_pick([("A", 7)], lots, 0) == [("A", "L2", 5), ("A", "L1", 2)]
'''
    },

    # 8. ALL THREE TARGET ISSUES (6 programs: P0495 - P0500)
    "P0495": {
        "domain": "Matrix & Grid Operations",
        "task": "Minimum-energy vertical seam for seam carving with protected cells",
        "category": "All three target issues",
        "code": '''def min_vertical_seam(energy: list[list[float]], protected: set[tuple[int, int]], penalty: float) -> tuple[float, list[int]]:
    rows, cols = len(energy), len(energy[0])
    cost = [row[:] for row in energy]
    for r in range(1, rows):
        for c in range(cols):
            candidates = [cost[r - 1][k] for k in (c - 1, c, c + 1) if 0 <= k < cols]
            cost[r][c] += min(candidates)
            if c == 0 or c == cols - 1 or (r, c) in protected:
                cost[r][c] += penalty
    seam = [min(range(cols), key=lambda k: cost[-1][k])]
    for r in range(rows - 2, -1, -1):
        prev = seam[-1]
        options = [k for k in (prev - 1, prev, prev + 1) if 0 <= k < cols]
        seam.append(min(options, key=lambda k: cost[r][k]))
    return cost[-1][seam[0]], seam[::-1]

if __name__ == "__main__":
    energy = [[1, 5, 1], [5, 1, 5], [1, 5, 1]]
    assert min_vertical_seam(energy, set(), 0.0) == (3, [0, 1, 0])
'''
    },
    "P0496": {
        "domain": "Data Aggregation and Statistics",
        "task": "Rolling-window z-score anomalies in smart meter readings",
        "category": "All three target issues",
        "code": '''import statistics

def rolling_zscore_anomalies(meters: dict[str, list[float]], window: int, z_limit: float) -> dict[str, list[int]]:
    anomalies = {}
    for meter, readings in meters.items():
        flagged = []
        for i in range(window, len(readings)):
            history = readings[i - window:i]
            spread = statistics.pstdev(history)
            z_score = (readings[i] - statistics.mean(history)) / spread if spread > 0 else 0.0
            if abs(z_score) > z_limit and readings[i] >= 0 and spread > 0:
                flagged.append(i)
        anomalies[meter] = flagged
    return anomalies

if __name__ == "__main__":
    meters = {"m1": [1.0, 2.0, 1.0, 2.0, 9.0], "m2": [1.0, 1.0, 1.0]}
    assert rolling_zscore_anomalies(meters, 4, 3.0) == {"m1": [4], "m2": []}
'''
    },
    "P0497": {
        "domain": "Inventory and Record Management",
        "task": "Slot fast-moving SKUs into the nearest pick locations under weight limits",
        "category": "All three target issues",
        "code": '''def assign_pick_slots(skus: list[tuple[str, int, float]], slots: list[tuple[str, int, float]]) -> dict[str, str]:
    taken = set()
    assignment = {}
    for sku, picks_per_day, unit_weight in sorted(skus, key=lambda s: -s[1]):
        for slot_id, distance_m, max_weight in sorted(slots, key=lambda s: s[1]):
            travel_cost_per_day = 2.0 * distance_m * picks_per_day / 1000.0 * (1.2 if unit_weight > 15 else 1.0)
            if slot_id not in taken and unit_weight <= max_weight and travel_cost_per_day < 50.0:
                assignment[sku] = slot_id
                taken.add(slot_id)
                break
    return assignment

if __name__ == "__main__":
    skus = [("A", 100, 2.0), ("B", 500, 20.0)]
    slots = [("S1", 5, 10.0), ("S2", 10, 25.0)]
    assert assign_pick_slots(skus, slots) == {"B": "S2", "A": "S1"}
'''
    },
    "P0498": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Sequence runway landings with wake separation and emergency priority",
        "category": "All three target issues",
        "code": '''def sequence_runway(flights: list[tuple[str, int, str, bool]], separation: dict[tuple[str, str], int]) -> list[tuple[str, int]]:
    schedule = []
    ordered = sorted(flights, key=lambda f: (not f[3], f[1]))
    for flight_id, eta, wake, emergency in ordered:
        slot = eta
        for prev_id, prev_time, prev_wake in schedule:
            gap_needed = separation.get((prev_wake, wake), 60) if not emergency else 30
            if slot < prev_time + gap_needed and slot >= prev_time - 30 and prev_id != flight_id:
                slot = prev_time + gap_needed
        schedule.append((flight_id, slot, wake))
    return [(fid, t) for fid, t, _ in schedule]

if __name__ == "__main__":
    flights = [("F1", 0, "H", False), ("F2", 30, "L", False)]
    flights.append(("E1", 60, "M", True))
    expected = [("E1", 60), ("F1", 0), ("F2", 180)]
    assert sequence_runway(flights, {("H", "L"): 180}) == expected
'''
    },
    "P0499": {
        "domain": "String Processing & Text Analysis",
        "task": "Spelling suggestions within one edit of dictionary words",
        "category": "All three target issues",
        "code": '''def spelling_suggestions(text: str, dictionary: set[str], max_suggestions: int = 3) -> dict[str, list[str]]:
    letters = "abcdefghijklmnopqrstuvwxyz"
    suggestions = {}
    for word in text.lower().split():
        if word in dictionary or not word.isalpha():
            continue
        candidates = set()
        for i in range(len(word) + 1):
            for ch in letters:
                candidates.add(word[:i] + ch + word[i:])
                if i < len(word) and ch != word[i] and word[:i] + ch + word[i + 1:] in dictionary:
                    candidates.add(word[:i] + ch + word[i + 1:])
            candidates.add(word[:i] + word[i + 1:])
        suggestions[word] = sorted(candidates & dictionary)[:max_suggestions]
    return suggestions

if __name__ == "__main__":
    words = {"cat", "cart", "coat", "at"}
    expected = {"cot": ["cat", "coat"], "ca": ["cat"]}
    assert spelling_suggestions("Cot ca", words) == expected
'''
    },
    "P0500": {
        "domain": "Graph or Tree Traversal",
        "task": "Maximum flow between two nodes with the Edmonds-Karp algorithm",
        "category": "All three target issues",
        "code": '''from collections import deque

def max_flow_value(capacity: dict[str, dict[str, int]], source: str, sink: str) -> int:
    residual = {u: dict(edges) for u, edges in capacity.items()}
    for u, edges in capacity.items():
        for v in edges:
            residual.setdefault(v, {}).setdefault(u, 0)
    flow = 0
    while True:
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            node = queue.popleft()
            for nxt, cap in residual[node].items():
                if cap > 0 and nxt not in parent and node != sink:
                    parent[nxt] = node
                    queue.append(nxt)
        if sink not in parent:
            return flow
        path = []
        v = sink
        while parent[v] is not None:
            path.append((parent[v], v))
            v = parent[v]
        augmenting_path_bottleneck_capacity = min(residual[u][v] for u, v in path)
        for u, v in path:
            residual[u][v] -= augmenting_path_bottleneck_capacity
            residual[v][u] += augmenting_path_bottleneck_capacity
        flow += augmenting_path_bottleneck_capacity

if __name__ == "__main__":
    cap = {"s": {"a": 3, "b": 2}, "b": {"t": 3}}
    cap["a"] = {"t": 2, "b": 1}
    assert max_flow_value(cap, "s", "t") == 5
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 10",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v10.0-expansion",
        "programs": BATCH10_PROGRAMS,
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