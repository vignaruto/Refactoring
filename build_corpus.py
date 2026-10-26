"""
build_corpus.py
Writes the Batch 14 (P0651-P0700) programs into program_corpus/programs and
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

BATCH14_PROGRAMS = {
    # 1. NONE (7 programs: P0651 - P0657)
    "P0651": {
        "domain": "Numerical Computation",
        "task": "Continued fraction terms of a rational number and its reconstruction",
        "category": "None",
        "code": '''def continued_fraction(numerator: int, denominator: int) -> list[int]:
    terms = []
    while denominator:
        whole, rest = divmod(numerator, denominator)
        terms.append(whole)
        numerator, denominator = denominator, rest
    return terms


def evaluate_fraction(terms: list[int]) -> tuple[int, int]:
    num, den = terms[-1], 1
    for term in reversed(terms[:-1]):
        num, den = term * num + den, num
    return num, den


if __name__ == "__main__":
    cf = continued_fraction(415, 93)
    assert cf == [4, 2, 6, 7]
    assert evaluate_fraction(cf) == (415, 93)
'''
    },
    "P0652": {
        "domain": "String Processing & Text Analysis",
        "task": "Run-length tokens such as 3a and their expansion back to text",
        "category": "None",
        "code": '''from itertools import groupby

def run_length_tokens(text):
    return [f"{len(list(g))}{ch}" for ch, g in groupby(text)]

def expand_tokens(tokens):
    parts = []
    for token in tokens:
        count, ch = int(token[:-1]), token[-1]
        parts.append(ch * count)
    return "".join(parts)

if __name__ == "__main__":
    toks = run_length_tokens("aaabccdddd")
    assert toks == ["3a", "1b", "2c", "4d"]
    assert expand_tokens(toks) == "aaabccdddd"
'''
    },
    "P0653": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Turn header plus row tuples into dict records, skipping ragged rows",
        "category": "None",
        "code": '''def rows_to_records(header: tuple, rows: list) -> list[dict]:
    records = []
    for row in rows:
        if len(row) != len(header):
            continue
        records.append(dict(zip(header, row)))
    return records


def column_values(records: list[dict], key: str) -> set:
    return {record[key] for record in records if key in record}


if __name__ == "__main__":
    header = ("id", "name")
    rows = [(1, "ann"), (2,), (3, "bo")]
    recs = rows_to_records(header, rows)
    assert recs == [{"id": 1, "name": "ann"}, {"id": 3, "name": "bo"}]
    assert column_values(recs, "name") == {"ann", "bo"}
'''
    },
    "P0654": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Deal tasks to workers in round-robin order and find the busiest worker",
        "category": "None",
        "code": '''def deal_tasks_round_robin(tasks, workers):
    plan = {worker: [] for worker in workers}
    for index, task in enumerate(tasks):
        worker = workers[index % len(workers)]
        plan[worker].append(task)
    return plan

def busiest_worker(plan):
    return max(plan, key=lambda w: (len(plan[w]), w))

if __name__ == "__main__":
    tasks = list("abcde")
    plan = deal_tasks_round_robin(tasks, ["x", "y"])
    assert plan == {"x": ["a", "c", "e"], "y": ["b", "d"]}
    assert busiest_worker(plan) == "x"
'''
    },
    "P0655": {
        "domain": "Inventory and Record Management",
        "task": "Restock quantities for SKUs under their reorder point and the order cost",
        "category": "None",
        "code": '''def restock_orders(stock: dict, reorder_point: dict, target: dict) -> dict:
    orders = {}
    for sku, qty in stock.items():
        if qty < reorder_point.get(sku, 0):
            orders[sku] = target[sku] - qty
    return orders


def order_cost(orders: dict, unit_cost: dict) -> float:
    total = 0.0
    for sku, qty in orders.items():
        total += qty * unit_cost[sku]
    return round(total, 2)


if __name__ == "__main__":
    stock = {"bolt": 4, "nut": 50, "washer": 0}
    points = {"bolt": 10, "nut": 20, "washer": 5}
    target = {"bolt": 40, "nut": 100, "washer": 30}
    orders = restock_orders(stock, points, target)
    assert orders == {"bolt": 36, "washer": 30}
    assert order_cost({"bolt": 36}, {"bolt": 0.25}) == 9.0
'''
    },
    "P0656": {
        "domain": "Data Aggregation and Statistics",
        "task": "Mid-rank percentile of every score within its own sample",
        "category": "None",
        "code": '''from bisect import bisect_left, bisect_right


def midrank_percentiles(scores):
    ordered = sorted(scores)
    n = len(ordered)
    ranks = []
    for score in scores:
        below = bisect_left(ordered, score)
        equal = bisect_right(ordered, score) - below
        ranks.append(round(100 * (below + 0.5 * equal) / n, 1))
    return ranks


if __name__ == "__main__":
    ranks = midrank_percentiles([50, 70, 70, 90])
    assert ranks == [12.5, 50.0, 50.0, 87.5]
'''
    },
    "P0657": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Heater on/off states from a thermostat with a hysteresis band",
        "category": "None",
        "code": '''def thermostat_states(temps, low=18.0, high=22.0):
    heating = False
    states = []
    for temp in temps:
        if temp < low:
            heating = True
        elif temp > high:
            heating = False
        states.append("on" if heating else "off")
    return states

if __name__ == "__main__":
    temps = [17, 19, 21, 23, 20, 17.5]
    expected = ["on", "on", "on", "off", "off", "on"]
    assert thermostat_states(temps) == expected
'''
    },

    # 2. NESTED LOOP ONLY (7 programs: P0658 - P0664)
    "P0658": {
        "domain": "Matrix & Grid Operations",
        "task": "Group matrix cells into anti-diagonals and find the heaviest one",
        "category": "Nested loop only",
        "code": '''def anti_diagonals(grid):
    rows, cols = len(grid), len(grid[0])
    diagonals = [[] for _ in range(rows + cols - 1)]
    for r in range(rows):
        for c in range(cols):
            diagonals[r + c].append(grid[r][c])
    return diagonals

def heaviest_diagonal(grid):
    sums = [sum(d) for d in anti_diagonals(grid)]
    return sums.index(max(sums))

if __name__ == "__main__":
    grid = [[1, 2, 3], [4, 5, 6]]
    assert anti_diagonals(grid) == [[1], [2, 4], [3, 5], [6]]
    assert heaviest_diagonal(grid) == 2
'''
    },
    "P0659": {
        "domain": "Graph or Tree Traversal",
        "task": "Number of distinct source-to-node paths in a DAG given a topological order",
        "category": "Nested loop only",
        "code": '''def count_dag_paths(graph: dict, order: list, source) -> dict:
    ways = {node: 0 for node in order}
    ways[source] = 1
    for node in order:
        for nxt in graph.get(node, []):
            ways[nxt] += ways[node]
    return ways


if __name__ == "__main__":
    graph = {"s": ["a", "b"], "a": ["t"], "b": ["a", "t"]}
    order = ["s", "b", "a", "t"]
    assert count_dag_paths(graph, order, "s")["t"] == 3
'''
    },
    "P0660": {
        "domain": "Searching and Sorting",
        "task": "Merge several sorted lists by repeatedly scanning the current heads",
        "category": "Nested loop only",
        "code": '''def scan_merge_sorted(lists):
    heads = [0] * len(lists)
    merged = []
    total = sum(len(lst) for lst in lists)
    while len(merged) < total:
        best = None
        for i, lst in enumerate(lists):
            if heads[i] >= len(lst):
                continue
            if best is None or lst[heads[i]] < lists[best][heads[best]]:
                best = i
        merged.append(lists[best][heads[best]])
        heads[best] += 1
    return merged

if __name__ == "__main__":
    parts = [[1, 4, 9], [2, 3], [], [5]]
    assert scan_merge_sorted(parts) == [1, 2, 3, 4, 5, 9]
'''
    },
    "P0661": {
        "domain": "String Processing & Text Analysis",
        "task": "Index each letter to its word and position, then letters in every word",
        "category": "Nested loop only",
        "code": '''def letter_positions(words):
    index = {}
    for w_idx, word in enumerate(words):
        for c_idx, ch in enumerate(word):
            index.setdefault(ch, []).append((w_idx, c_idx))
    return index

def letters_in_every_word(index, word_count):
    shared = []
    for ch, spots in index.items():
        if len({w for w, _ in spots}) == word_count:
            shared.append(ch)
    return sorted(shared)

if __name__ == "__main__":
    idx = letter_positions(["ab", "ba"])
    assert idx == {"a": [(0, 0), (1, 1)], "b": [(0, 1), (1, 0)]}
    words = ["stone", "notes", "tone"]
    assert letters_in_every_word(letter_positions(words), 3) == list("enot")
'''
    },
    "P0662": {
        "domain": "Data Aggregation and Statistics",
        "task": "Cross-tabulate two categorical fields and compute row shares",
        "category": "Nested loop only",
        "code": '''def cross_tab(rows, row_key, col_key):
    row_labels = sorted({r[row_key] for r in rows})
    col_labels = sorted({r[col_key] for r in rows})
    table = {a: {b: 0 for b in col_labels} for a in row_labels}
    for record in rows:
        table[record[row_key]][record[col_key]] += 1
    return table


def row_shares(table):
    shares = {}
    for a, counts in table.items():
        total = sum(counts.values())
        for b, n in counts.items():
            shares[(a, b)] = round(n / total, 3) if total else 0.0
    return shares


if __name__ == "__main__":
    rows = [{"g": "x", "r": "yes"}, {"g": "x", "r": "no"}]
    rows.append({"g": "y", "r": "yes"})
    table = cross_tab(rows, "g", "r")
    assert table == {"x": {"no": 1, "yes": 1}, "y": {"no": 0, "yes": 1}}
    assert row_shares(table)[("x", "yes")] == 0.5
'''
    },
    "P0663": {
        "domain": "Numerical Computation",
        "task": "Count integer lattice points inside a circle and estimate pi from them",
        "category": "Nested loop only",
        "code": '''def lattice_points_in_circle(radius: int) -> int:
    count = 0
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if x * x + y * y <= radius * radius:
                count += 1
    return count


def estimate_pi(radius: int) -> float:
    return lattice_points_in_circle(radius) / radius ** 2


if __name__ == "__main__":
    assert lattice_points_in_circle(1) == 5
    assert lattice_points_in_circle(2) == 13
    assert abs(estimate_pi(50) - 3.14159) < 0.05
'''
    },
    "P0664": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Swap the outer and inner keys of a nested dictionary",
        "category": "Nested loop only",
        "code": '''def transpose_mapping(outer):
    flipped = {}
    for key, inner in outer.items():
        for sub_key, value in inner.items():
            flipped.setdefault(sub_key, {})[key] = value
    return flipped

if __name__ == "__main__":
    scores = {"a": {"x": 1, "y": 2}, "b": {"x": 3}}
    flipped = transpose_mapping(scores)
    assert flipped == {"x": {"a": 1, "b": 3}, "y": {"a": 2}}
'''
    },

    # 3. COMPLEX CONDITIONAL ONLY (7 programs: P0665 - P0671)
    "P0665": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Pedestrian crossing phases over time from button presses",
        "category": "Complex conditional only",
        "code": '''def crossing_timeline(presses, min_green=10, max_green=30, walk_time=5):
    phase, timer, waiting = "green", 0, False
    timeline = []
    for pressed in presses:
        timer += 1
        waiting = waiting or pressed
        if phase == "green" and (waiting and timer >= min_green or timer >= max_green):
            phase, timer, waiting = "walk", 0, False
        elif phase == "walk" and timer >= walk_time:
            phase, timer = "green", 0
        timeline.append(phase)
    return timeline

if __name__ == "__main__":
    presses = [False] * 3 + [True] + [False] * 10
    timeline = crossing_timeline(presses, 4, 30, 2)
    assert timeline[:6] == ["green"] * 3 + ["walk", "walk", "green"]
    idle = crossing_timeline([False] * 5, 1, 3, 1)
    assert idle == ["green", "green", "walk", "green", "green"]
'''
    },
    "P0666": {
        "domain": "Inventory and Record Management",
        "task": "Whether a stock lot may ship given quantity, shelf life and quality hold",
        "category": "Complex conditional only",
        "code": '''def can_ship_lot(lot: dict, today: int, min_shelf_days: int = 30) -> bool:
    remaining = lot["expiry_day"] - today
    on_hold = lot.get("quality_hold", False)
    if lot["qty"] > 0 and remaining >= min_shelf_days and not on_hold:
        return True
    return False


if __name__ == "__main__":
    lot = {"qty": 5, "expiry_day": 100}
    assert can_ship_lot(lot, 50)
    assert not can_ship_lot(lot, 80)
    assert not can_ship_lot({**lot, "quality_hold": True}, 50)
'''
    },
    "P0667": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Fill a shift with highest-priority tasks until hours or budget run out",
        "category": "Complex conditional only",
        "code": '''def fill_shift_by_priority(tasks, rate, max_hours, budget):
    queue = sorted(tasks, key=lambda t: (-t[2], t[1]))
    plan = []
    hours = 0
    cost = 0
    while queue and hours + queue[0][1] <= max_hours and cost + queue[0][1] * rate <= budget:
        name, duration, priority = queue.pop(0)
        plan.append(name)
        hours += duration
        cost += duration * rate
    leftover = [name for name, _, _ in queue]
    return plan, hours, leftover

if __name__ == "__main__":
    tasks = [("a", 2, 1), ("b", 3, 5), ("c", 4, 5)]
    assert fill_shift_by_priority(tasks, 10, 8, 100) == (["b", "c"], 7, ["a"])
    assert fill_shift_by_priority(tasks, 10, 20, 50) == (["b"], 3, ["c", "a"])
'''
    },
    "P0668": {
        "domain": "String Processing & Text Analysis",
        "task": "Markdown heading level of a line, or 0 when it is not a heading",
        "category": "Complex conditional only",
        "code": '''def heading_level(line):
    stripped = line.lstrip()
    hashes = len(stripped) - len(stripped.lstrip("#"))
    rest = stripped[hashes:]
    if 1 <= hashes <= 6 and rest.startswith(" ") and rest.strip():
        return hashes
    return 0

if __name__ == "__main__":
    assert heading_level("## Title") == 2
    assert heading_level("####### deep") == 0
    assert heading_level("#nospace") == 0
    assert heading_level("#   ") == 0
'''
    },
    "P0669": {
        "domain": "Graph or Tree Traversal",
        "task": "Check a node-table tree obeys binary search tree bounds without cycles",
        "category": "Complex conditional only",
        "code": '''def is_search_tree(tree: dict, root) -> bool:
    visited = set()
    stack = [(root, float("-inf"), float("inf"))]
    while stack:
        node, low, high = stack.pop()
        if node is None:
            continue
        value, left, right = tree[node]
        if not low < value < high or node in visited:
            return False
        visited.add(node)
        stack.append((left, low, value))
        stack.append((right, value, high))
    return True


if __name__ == "__main__":
    good = {"r": (5, "a", "b")}
    good["a"] = (3, None, None)
    good["b"] = (8, None, None)
    bad = {"r": (5, "a", None), "a": (7, None, None)}
    assert is_search_tree(good, "r")
    assert not is_search_tree(bad, "r")
'''
    },
    "P0670": {
        "domain": "Searching and Sorting",
        "task": "First product that is in stock, within budget and rated highly enough",
        "category": "Complex conditional only",
        "code": '''def first_affordable(products, max_price, min_rating):
    for index, (name, price, rating, stock) in enumerate(products):
        if price <= max_price and rating >= min_rating and stock > 0:
            return index, name
    return -1, None

if __name__ == "__main__":
    items = [("lamp", 30, 4.5, 0), ("desk", 120, 4.8, 3)]
    items.append(("chair", 45, 4.2, 7))
    assert first_affordable(items, 50, 4.0) == (2, "chair")
    assert first_affordable(items, 20, 4.0) == (-1, None)
'''
    },
    "P0671": {
        "domain": "Numerical Computation",
        "task": "Check whether a numeric sequence is a geometric progression",
        "category": "Complex conditional only",
        "code": '''def is_geometric(seq: list[float], rel_tol: float = 1e-9) -> bool:
    if len(seq) < 2:
        return True
    if seq[0] == 0:
        return all(x == 0 for x in seq)
    ratio = seq[1] / seq[0]
    for prev, cur in zip(seq, seq[1:]):
        if prev == 0 or cur == 0 or abs(cur / prev - ratio) > rel_tol:
            return False
    return True


if __name__ == "__main__":
    assert is_geometric([3, 6, 12, 24])
    assert not is_geometric([1, 2, 4, 7])
    assert is_geometric([5])
    assert is_geometric([0, 0])
    assert not is_geometric([2, 0, 0])
'''
    },

    # 4. LONG STATEMENT ONLY (7 programs: P0672 - P0678)
    "P0672": {
        "domain": "Numerical Computation",
        "task": "Future value of a principal plus monthly deposits, ordinary or due",
        "category": "Long statement only",
        "code": '''def savings_value(principal, deposit, annual_rate, years, due=0):
    rate = annual_rate / 12
    n = years * 12
    if rate == 0:
        return round(principal + deposit * n, 2)
    growth = (1 + rate) ** n
    value = principal * growth + deposit * (growth - 1) / rate * (1 + rate * due)
    return round(value, 2)

if __name__ == "__main__":
    assert savings_value(1000, 0, 0.0, 5) == 1000
    assert savings_value(0, 100, 0.0, 1) == 1200
    assert savings_value(1000, 0, 0.12, 1) == 1126.83
'''
    },
    "P0673": {
        "domain": "Data Aggregation and Statistics",
        "task": "Combined mean and standard deviation from per-group count, mean and std",
        "category": "Long statement only",
        "code": '''from math import sqrt

def pooled_summary(groups):
    total = sum(n for n, _, _ in groups)
    mean = sum(n * m for n, m, _ in groups) / total
    within = sum((n - 1) * s ** 2 for n, _, s in groups)
    between = sum(n * (m - mean) ** 2 for n, m, _ in groups)
    return round(mean, 3), round(sqrt((within + between) / (total - 1)), 3)

if __name__ == "__main__":
    groups = [(2, 1.0, 0.0), (2, 3.0, 0.0)]
    assert pooled_summary(groups) == (2.0, 1.155)
'''
    },
    "P0674": {
        "domain": "Inventory and Record Management",
        "task": "Inventory valuation including freight and duty on imported lines",
        "category": "Long statement only",
        "code": '''def inventory_valuation(items, freight_rate=0.05, duty_rate=0.1):
    total = 0.0
    for item in items:
        base = item["qty"] * item["unit_cost"]
        total += base + base * freight_rate + base * duty_rate * item.get("imported", 0)
    return round(total, 2)

if __name__ == "__main__":
    local = {"qty": 10, "unit_cost": 2.0}
    imported = {"qty": 1, "unit_cost": 100.0, "imported": 1}
    assert inventory_valuation([local, imported]) == 136.0
    assert inventory_valuation([]) == 0.0
'''
    },
    "P0675": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Meeting agenda with clock times, gaps and a flag for long items",
        "category": "Long statement only",
        "code": '''def hhmm(minute):
    return f"{minute // 60:02d}:{minute % 60:02d}"


def build_agenda(start_minute, items, gap=5):
    agenda = []
    clock = start_minute
    for title, minutes in items:
        agenda.append((hhmm(clock), hhmm(clock + minutes), title, minutes >= 30))
        clock += minutes + gap
    return agenda


if __name__ == "__main__":
    items = [("intro", 10), ("review", 45)]
    agenda = build_agenda(540, items)
    assert agenda[0] == ("09:00", "09:10", "intro", False)
    assert agenda[1] == ("09:15", "10:00", "review", True)
'''
    },
    "P0676": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Horizontal range of a projectile launched from a given height",
        "category": "Long statement only",
        "code": '''import math

def projectile_range(speed, angle_deg, height=0.0, gravity=9.81):
    angle = math.radians(angle_deg)
    vx = speed * math.cos(angle)
    vy = speed * math.sin(angle)
    flight_time = (vy + math.sqrt(vy ** 2 + 2 * gravity * height)) / gravity
    return round(vx * flight_time, 2)

if __name__ == "__main__":
    assert projectile_range(10, 45) == 10.19
    assert projectile_range(10, 0, height=4.905) == 10.0
'''
    },
    "P0677": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Jaccard index and a blended set-similarity score for two tag sets",
        "category": "Long statement only",
        "code": '''def tag_similarity(tags_a: set, tags_b: set) -> tuple:
    if not tags_a or not tags_b:
        return 0.0, 0.0
    shared = len(tags_a & tags_b)
    union = len(tags_a | tags_b)
    dice = 2 * shared / (len(tags_a) + len(tags_b))
    blended = (shared / union + shared / min(len(tags_a), len(tags_b)) + dice) / 3
    jaccard = shared / union
    return round(jaccard, 3), round(blended, 3)


if __name__ == "__main__":
    assert tag_similarity({"x", "y"}, {"y", "z"}) == (0.333, 0.444)
    assert tag_similarity(set(), {"y"}) == (0.0, 0.0)
'''
    },
    "P0678": {
        "domain": "String Processing & Text Analysis",
        "task": "Score a username suggestion by letters, digits, length and availability",
        "category": "Long statement only",
        "code": '''def username_score(name: str, taken: set) -> int:
    digits = sum(ch.isdigit() for ch in name)
    letters = sum(ch.isalpha() for ch in name)
    penalty = 50 if name in taken else 0
    score = letters * 3 - digits * 2 - abs(len(name) - 8) * 4 - penalty + name.islower() * 5
    return score


if __name__ == "__main__":
    assert username_score("anna", set()) == 1
    assert username_score("bob12345", {"bob12345"}) == -46
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (7 programs: P0679 - P0685)
    "P0679": {
        "domain": "Matrix & Grid Operations",
        "task": "Weighted smoothing of interior grid cells using their four neighbours",
        "category": "Long statement and nested loop",
        "code": '''def smooth_interior(grid):
    rows, cols = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            edge = grid[r - 1][c] + grid[r + 1][c] + grid[r][c - 1] + grid[r][c + 1]
            out[r][c] = (4 * grid[r][c] + 2 * edge) / 12
    return out

if __name__ == "__main__":
    grid = [[1, 1, 1], [1, 4, 1], [1, 1, 1]]
    assert smooth_interior(grid)[1][1] == 2.0
    assert smooth_interior(grid)[0] == [1, 1, 1]
'''
    },
    "P0680": {
        "domain": "Graph or Tree Traversal",
        "task": "Edge weight inside versus across clusters of an undirected graph",
        "category": "Long statement and nested loop",
        "code": '''def cluster_edge_weights(graph, cluster_of):
    inside = 0.0
    crossing = 0.0
    for node, edges in graph.items():
        for neighbour, weight in edges:
            if cluster_of[node] == cluster_of[neighbour]:
                inside += weight
            else:
                crossing += weight
    cohesion = (inside - crossing) / (inside + crossing) if inside + crossing else 0.0
    return inside / 2, crossing / 2, round(cohesion, 3)

if __name__ == "__main__":
    graph = {"a": [("b", 1)], "c": [("b", 2)]}
    graph["b"] = [("a", 1), ("c", 2)]
    clusters = {"a": 0, "b": 0, "c": 1}
    assert cluster_edge_weights(graph, clusters) == (1.0, 2.0, -0.333)
'''
    },
    "P0681": {
        "domain": "Searching and Sorting",
        "task": "Rank documents for a query with a title boost for longer terms",
        "category": "Long statement and nested loop",
        "code": '''def rank_documents(docs, query_terms, title_boost=2.0):
    scored = []
    for doc_id, title, body in docs:
        score = 0.0
        for term in query_terms:
            score = score + body.count(term) + title_boost * title.count(term) * len(term) / 4
        scored.append((-score, doc_id))
    return [doc_id for _, doc_id in sorted(scored)]

if __name__ == "__main__":
    docs = [("d1", "cats", "cats and dogs")]
    docs.append(("d2", "dogs", "dogs dogs"))
    assert rank_documents(docs, ["dogs"]) == ["d2", "d1"]
    assert rank_documents(docs, ["cat"]) == ["d1", "d2"]
'''
    },
    "P0682": {
        "domain": "Data Aggregation and Statistics",
        "task": "Rolling-window maxima per named series and the spread of those peaks",
        "category": "Long statement and nested loop",
        "code": '''def rolling_peaks(series_by_name, window):
    peaks = {}
    for name, values in series_by_name.items():
        row = []
        for start in range(len(values) - window + 1):
            row.append(max(values[start:start + window]))
        peaks[name] = row
    return peaks


def peak_spread(peaks):
    return {name: round(max(row) - min(row), 2) if row else 0.0 for name, row in peaks.items()}


if __name__ == "__main__":
    peaks = rolling_peaks({"a": [1, 3, 2, 5], "b": [4]}, 2)
    assert peaks == {"a": [3, 3, 5], "b": []}
    assert peak_spread(peaks) == {"a": 2, "b": 0.0}
'''
    },
    "P0683": {
        "domain": "Inventory and Record Management",
        "task": "Free bin capacity per warehouse, ignoring quarantined X bins",
        "category": "Long statement and nested loop",
        "code": '''def spare_capacity(warehouses):
    report = {}
    for site, bins in warehouses.items():
        free = 0
        for bin_id, capacity, stored, reserved in bins:
            free = free + max(capacity - stored - reserved, 0) * (1 if bin_id[0] != "X" else 0)
        report[site] = free
    return report

if __name__ == "__main__":
    north = [("A1", 10, 4, 1), ("X2", 10, 0, 0)]
    south = [("B1", 5, 6, 0)]
    report = spare_capacity({"north": north, "south": south})
    assert report == {"north": 5, "south": 0}
'''
    },
    "P0684": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Free time slots per room and day given a set of bookings",
        "category": "Long statement and nested loop",
        "code": '''def room_timetable(rooms, days, n_slots, booked):
    table = []
    for day in days:
        for room in rooms:
            taken = {s for d, r, s in booked if d == day and r == room}
            free = [s for s in range(n_slots) if s not in taken]
            table.append({"day": day, "room": room, "free": free, "full": not free})
    return table

if __name__ == "__main__":
    booked = {("mon", "r1", 0), ("tue", "r1", 0)}
    booked.add(("tue", "r1", 1))
    table = room_timetable(["r1"], ["mon", "tue"], 2, booked)
    assert table[0]["free"] == [1]
    assert table[1]["full"]
'''
    },
    "P0685": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Pairwise agreement score between user preference dictionaries",
        "category": "Long statement and nested loop",
        "code": '''def profile_overlap(profiles):
    names = sorted(profiles)
    scores = {}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            keys = profiles[a].keys() & profiles[b].keys()
            if not keys:
                continue
            agree = sum(profiles[a][k] == profiles[b][k] for k in keys)
            score = agree / len(keys) * 0.7 + len(keys) / len(profiles[a].keys() | profiles[b].keys()) * 0.3
            scores[(a, b)] = round(score, 3)
    return scores

if __name__ == "__main__":
    profiles = {"ann": {"x": 1, "y": 2}}
    profiles["bob"] = {"x": 1, "z": 3}
    profiles["cy"] = {"q": 0}
    assert profile_overlap(profiles) == {("ann", "bob"): 0.8}
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (1 program: P0686)
    "P0686": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Wildfire danger rating from weather readings and dry days",
        "category": "Long statement and complex conditional",
        "code": '''def fire_risk(temperature, humidity, wind_speed, days_without_rain):
    index = temperature * 0.6 - humidity * 0.4 + wind_speed * 1.5 + days_without_rain * 2
    if index > 40 and humidity < 30 or wind_speed > 50:
        return "extreme", round(index, 1)
    if index > 25:
        return "high", round(index, 1)
    return "low", round(index, 1)

if __name__ == "__main__":
    assert fire_risk(35, 20, 10, 5) == ("high", 38.0)
    assert fire_risk(40, 10, 20, 10) == ("extreme", 70.0)
    assert fire_risk(10, 80, 5, 0) == ("low", -18.5)
    assert fire_risk(10, 80, 60, 0) == ("extreme", 64.0)
'''
    },

    # 7. ALL THREE TARGET ISSUES (7 programs: P0687 - P0693)
    "P0687": {
        "domain": "Matrix & Grid Operations",
        "task": "Local height peaks above a minimum with a prominence score",
        "category": "All three target issues",
        "code": '''def local_peaks(grid, min_height):
    rows, cols = len(grid), len(grid[0])
    peaks = []
    for r in range(rows):
        row = grid[r]
        for c in range(cols):
            h = row[c]
            up = grid[r - 1][c] if r > 0 else -1
            down = grid[r + 1][c] if r < rows - 1 else -1
            left = row[c - 1] if c > 0 else -1
            right = row[c + 1] if c < cols - 1 else -1
            if h >= min_height and h > max(up, down) and h > max(left, right):
                score = (h - max(up, down, left, right, 0)) * 2 + (h - min_height) / max(h, 1)
                peaks.append((r, c, round(score, 2)))
    return peaks

if __name__ == "__main__":
    grid = [[1, 2, 1], [2, 9, 2], [1, 2, 1]]
    assert local_peaks(grid, 5) == [(1, 1, 14.44)]
    assert local_peaks(grid, 10) == []
'''
    },
    "P0688": {
        "domain": "Graph or Tree Traversal",
        "task": "Cheapest route with banned nodes, toll fees and a hop limit",
        "category": "All three target issues",
        "code": '''import heapq

def cheapest_route(graph, start, goal, banned, tolls, max_hops, surcharge=0.0, toll_fee=5):
    best = {start: 0}
    heap = [(0, 0, start)]
    while heap:
        dist, hops, node = heapq.heappop(heap)
        if node == goal:
            return dist
        if dist > best.get(node, float("inf")):
            continue
        for nxt, weight in graph.get(node, []):
            cost = dist + weight * (1 + surcharge) + toll_fee * (nxt in tolls)
            if nxt in banned or hops >= max_hops or cost >= best.get(nxt, float("inf")):
                continue
            best[nxt] = cost
            heapq.heappush(heap, (cost, hops + 1, nxt))
    return None

if __name__ == "__main__":
    graph = {"a": [("b", 1), ("c", 4)]}
    graph["b"] = [("c", 1), ("d", 5)]
    graph["c"] = [("d", 1)]
    assert cheapest_route(graph, "a", "d", set(), set(), 5) == 3
    assert cheapest_route(graph, "a", "d", {"c"}, set(), 5) == 6
    assert cheapest_route(graph, "a", "d", set(), {"c"}, 5) == 6
    assert cheapest_route(graph, "a", "d", set(), set(), 1) is None
'''
    },
    "P0689": {
        "domain": "Searching and Sorting",
        "task": "Interpolation search for several queries in a sorted list",
        "category": "All three target issues",
        "code": '''def interpolation_lookup(sorted_values, queries):
    results = {}
    for query in queries:
        lo, hi = 0, len(sorted_values) - 1
        results[query] = -1
        while lo <= hi and sorted_values[lo] <= query <= sorted_values[hi]:
            if sorted_values[hi] == sorted_values[lo]:
                probe = lo
            else:
                probe = lo + (query - sorted_values[lo]) * (hi - lo) // (sorted_values[hi] - sorted_values[lo])
            if sorted_values[probe] == query:
                results[query] = probe
                break
            if sorted_values[probe] < query:
                lo = probe + 1
            else:
                hi = probe - 1
    return results

if __name__ == "__main__":
    values = [2, 4, 8, 16, 32, 64]
    found = interpolation_lookup(values, [16, 5, 2, 64])
    assert found == {16: 3, 5: -1, 2: 0, 64: 5}
'''
    },
    "P0690": {
        "domain": "Data Aggregation and Statistics",
        "task": "Flag z-score outliers inside each group of measurements",
        "category": "All three target issues",
        "code": '''def group_outliers(groups: dict, z_limit: float = 2.0) -> dict:
    flagged = {}
    for name, values in groups.items():
        n = len(values)
        mean = sum(values) / n
        spread = (sum((v - mean) ** 2 for v in values) / max(n - 1, 1)) ** 0.5
        hits = []
        for v in values:
            if spread > 0 and abs(v - mean) / spread > z_limit and n >= 3:
                hits.append(v)
        flagged[name] = hits
    return flagged


if __name__ == "__main__":
    a = [10, 10, 10, 10, 10, 10, 10, 10, 10, 100]
    groups = {"a": a, "b": [1, 2], "c": [5, 5, 5]}
    result = group_outliers(groups)
    assert result == {"a": [100], "b": [], "c": []}
'''
    },
    "P0691": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Assign jobs to the least-loaded machine meeting GPU and deadline needs",
        "category": "All three target issues",
        "code": '''def assign_jobs(jobs, machines):
    load = {m: 0 for m, _, _ in machines}
    plan = {}
    for job, hours, needs_gpu, deadline in jobs:
        choice = None
        for machine, has_gpu, capacity in machines:
            fits = load[machine] + hours <= capacity
            if fits and (has_gpu or not needs_gpu) and load[machine] + hours <= deadline:
                if choice is None or load[machine] < load[choice]:
                    choice = machine
        if choice is None:
            plan[job] = None
            continue
        load[choice] += hours
        plan[job] = (choice, load[choice] - hours, load[choice])
    return plan, sum(load.values()) / max(len(load), 1), max(load.values(), default=0)

if __name__ == "__main__":
    machines = [("m1", False, 8), ("g1", True, 8)]
    jobs = [("train", 4, True, 10), ("etl", 3, False, 10)]
    jobs.append(("report", 2, False, 3))
    plan, mean_load, peak = assign_jobs(jobs, machines)
    assert plan["train"] == ("g1", 0, 4)
    assert plan["etl"] == ("m1", 0, 3)
    assert plan["report"] is None
    assert (mean_load, peak) == (3.5, 4)
'''
    },
    "P0692": {
        "domain": "Numerical Computation",
        "task": "Midpoint-rule integral over the positive quadrant of a disc",
        "category": "All three target issues",
        "code": '''import math

def quadrant_integral(func, bounds, steps, radius, exact=0.0):
    (x0, x1), (y0, y1) = bounds
    dx = (x1 - x0) / steps
    dy = (y1 - y0) / steps
    r2 = radius * radius
    total = 0.0
    for i in range(steps):
        x = x0 + (i + 0.5) * dx
        for j in range(steps):
            y = y0 + (j + 0.5) * dy
            if x * x + y * y <= r2 and x >= 0 and y >= 0:
                total += func(x, y) * dx * dy
    return round(total, 4), round(abs(total - exact) / exact * 100, 2) if exact else 0.0

if __name__ == "__main__":
    bounds = ((-1.0, 1.0), (-1.0, 1.0))
    exact = math.pi / 4
    unit = lambda x, y: 1.0
    result = quadrant_integral(unit, bounds, 200, 1.0, exact)
    area, err = result
    assert abs(area - exact) < 0.01
    assert err < 1
'''
    },
    "P0693": {
        "domain": "Inventory and Record Management",
        "task": "Reconcile counted stock against book records with value of each gap",
        "category": "All three target issues",
        "code": '''def reconcile_counts(system: dict, counted: dict, prices: dict, tolerance: int = 2, handling_fee: float = 1.5) -> list:
    issues = []
    for location, items in counted.items():
        expected = system.get(location, {})
        for sku, qty in items.items():
            book = expected.get(sku, 0)
            gap = qty - book
            if abs(gap) > tolerance and book > 0 or sku not in expected:
                value_gap = gap * prices.get(sku, 0.0) + (handling_fee if gap < 0 else 0.0)
                issues.append((location, sku, gap, round(value_gap, 2)))
    return sorted(issues)


if __name__ == "__main__":
    system = {"A": {"x": 10, "y": 5}}
    counted = {"A": {"x": 7, "y": 5, "z": 1}}
    prices = {"x": 2.0, "z": 3.0}
    issues = reconcile_counts(system, counted, prices)
    assert issues == [("A", "x", -3, -4.5), ("A", "z", 1, 3.0)]
'''
    },

    # 8. NESTED LOOP AND COMPLEX CONDITIONAL (7 programs: P0694 - P0700)
    "P0694": {
        "domain": "Matrix & Grid Operations",
        "task": "Centres of plus-shaped patterns of filled cells in a binary grid",
        "category": "Nested loop and complex conditional",
        "code": '''def plus_centres(grid):
    rows, cols = len(grid), len(grid[0])
    centres = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if grid[r][c] and grid[r - 1][c] and grid[r + 1][c]:
                if grid[r][c - 1] and grid[r][c + 1]:
                    centres.append((r, c))
    return centres

if __name__ == "__main__":
    plus = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    tee = [[0, 1, 0], [1, 1, 0], [0, 1, 0]]
    assert plus_centres(plus) == [(1, 1)]
    assert plus_centres(tee) == []
'''
    },
    "P0695": {
        "domain": "Graph or Tree Traversal",
        "task": "Count triangles in an undirected graph given as adjacency sets",
        "category": "Nested loop and complex conditional",
        "code": '''def count_triangles(adj: dict) -> int:
    nodes = sorted(adj)
    total = 0
    for i, a in enumerate(nodes):
        for b in nodes[i + 1:]:
            for c in adj[a]:
                if b < c and b in adj[a] and c in adj[b]:
                    total += 1
    return total


if __name__ == "__main__":
    adj = {1: {2, 3, 4}, 2: {1, 3}, 3: {1, 2}, 4: {1}}
    assert count_triangles(adj) == 1
    assert count_triangles({1: {2}, 2: {1}}) == 0
'''
    },
    "P0696": {
        "domain": "Searching and Sorting",
        "task": "Count rising index triples whose consecutive gaps stay within a limit",
        "category": "Nested loop and complex conditional",
        "code": '''def rising_triples(values, max_gap):
    count = 0
    n = len(values)
    for i in range(n):
        for j in range(i + 1, n):
            if values[j] <= values[i] or values[j] - values[i] > max_gap:
                continue
            for k in range(j + 1, n):
                if values[i] < values[j] < values[k] and values[k] - values[j] <= max_gap:
                    count += 1
    return count

if __name__ == "__main__":
    assert rising_triples([1, 2, 3, 4], 1) == 2
    assert rising_triples([1, 2, 3, 4], 5) == 4
    assert rising_triples([3, 2, 1], 5) == 0
'''
    },
    "P0697": {
        "domain": "String Processing & Text Analysis",
        "task": "Find accidentally doubled words on each line of a text",
        "category": "Nested loop and complex conditional",
        "code": '''def repeated_line_words(lines, min_length=3):
    hits = []
    for number, line in enumerate(lines, start=1):
        words = line.lower().split()
        for i in range(1, len(words)):
            word = words[i]
            if word == words[i - 1] and len(word) >= min_length and word.isalpha():
                hits.append((number, word))
    return hits

if __name__ == "__main__":
    lines = ["The the cat", "go go go", "a a"]
    hits = repeated_line_words(lines, 2)
    assert hits == [(1, "the"), (2, "go"), (2, "go")]
'''
    },
    "P0698": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Scalar settings shared with the same value by every config dictionary",
        "category": "Nested loop and complex conditional",
        "code": '''def common_settings(configs):
    if not configs:
        return {}
    shared = {}
    for key, value in configs[0].items():
        agreed = True
        for other in configs[1:]:
            if key not in other or other[key] != value or isinstance(value, dict):
                agreed = False
                break
        if agreed:
            shared[key] = value
    return shared

if __name__ == "__main__":
    first = {"a": 1, "b": 2, "c": {}}
    second = {"a": 1, "b": 3, "c": {}}
    assert common_settings([first, second]) == {"a": 1}
    assert common_settings([]) == {}
'''
    },
    "P0699": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Topple an abelian sandpile grid until every cell is stable",
        "category": "Nested loop and complex conditional",
        "code": '''def topple_sandpile(grid):
    cells = [row[:] for row in grid]
    rows, cols = len(cells), len(cells[0])
    rounds = 0
    changed = True
    while changed:
        changed = False
        for r in range(rows):
            for c in range(cols):
                if cells[r][c] < 4:
                    continue
                changed = True
                cells[r][c] -= 4
                for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols:
                        cells[nr][nc] += 1
        rounds += 1
    return cells, rounds

if __name__ == "__main__":
    grid = [[0, 0, 0], [0, 4, 0], [0, 0, 0]]
    cells, rounds = topple_sandpile(grid)
    assert cells == [[0, 1, 0], [1, 0, 1], [0, 1, 0]]
    assert rounds == 2
'''
    },
    "P0700": {
        "domain": "Matrix & Grid Operations",
        "task": "Count axis-aligned rectangles whose four corner cells hold equal values",
        "category": "Nested loop and complex conditional",
        "code": '''def equal_corner_rectangles(grid):
    rows, cols = len(grid), len(grid[0])
    count = 0
    for top in range(rows):
        for bottom in range(top + 1, rows):
            for left in range(cols):
                for right in range(left + 1, cols):
                    v = grid[top][left]
                    if v == grid[top][right] and v == grid[bottom][left] and v == grid[bottom][right]:
                        count += 1
    return count

if __name__ == "__main__":
    assert equal_corner_rectangles([[1, 1], [1, 1]]) == 1
    assert equal_corner_rectangles([[1, 1, 1], [1, 1, 1]]) == 3
    assert equal_corner_rectangles([[1, 2], [2, 1]]) == 0
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 14",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v14.0-expansion",
        "programs": BATCH14_PROGRAMS,
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