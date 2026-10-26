"""
build_corpus.py
Writes the Batch 15 (P0701-P0750) programs into program_corpus/programs and
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

BATCH15_PROGRAMS = {
    # 1. NESTED LOOP ONLY (7 programs: P0701 - P0707)
    "P0701": {
        "domain": "Numerical Computation",
        "task": "Divisor counts by a multiples sieve and the highly composite numbers",
        "category": "Nested loop only",
        "code": '''def divisor_counts(limit: int) -> list[int]:
    counts = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for multiple in range(d, limit + 1, d):
            counts[multiple] += 1
    return counts


def highly_composite_upto(limit: int) -> list[int]:
    counts = divisor_counts(limit)
    record = 0
    found = []
    for n in range(1, limit + 1):
        if counts[n] > record:
            record = counts[n]
            found.append(n)
    return found


if __name__ == "__main__":
    assert divisor_counts(6)[1:] == [1, 2, 2, 3, 2, 4]
    expected = [1, 2, 4, 6, 12, 24, 36, 48, 60]
    assert highly_composite_upto(60) == expected
'''
    },
    "P0702": {
        "domain": "String Processing & Text Analysis",
        "task": "Letter-to-next-letter transition counts and the likeliest follower",
        "category": "Nested loop only",
        "code": '''def transition_counts(words):
    table = {}
    for word in words:
        for first, second in zip(word, word[1:]):
            row = table.setdefault(first, {})
            row[second] = row.get(second, 0) + 1
    return table

def likeliest_next(table, ch):
    row = table.get(ch, {})
    return max(sorted(row), key=row.get) if row else None

if __name__ == "__main__":
    table = transition_counts(["abab", "ac"])
    assert table == {"a": {"b": 2, "c": 1}, "b": {"a": 1}}
    assert likeliest_next(table, "a") == "b"
    assert likeliest_next(table, "z") is None
'''
    },
    "P0703": {
        "domain": "Graph or Tree Traversal",
        "task": "Set of nodes reachable from every node by breadth-first search",
        "category": "Nested loop only",
        "code": '''from collections import deque

def reachable_sets(graph):
    reach = {}
    for start in graph:
        seen = {start}
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nxt in graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        reach[start] = seen - {start}
    return reach

if __name__ == "__main__":
    graph = {"a": ["b"], "b": ["c"], "c": [], "d": ["a"]}
    reach = reachable_sets(graph)
    assert reach["a"] == {"b", "c"}
    assert reach["c"] == set()
    assert reach["d"] == {"a", "b", "c"}
'''
    },
    "P0704": {
        "domain": "Matrix & Grid Operations",
        "task": "Two-dimensional prefix-sum table and rectangle sums from it",
        "category": "Nested loop only",
        "code": '''def prefix_table(grid):
    rows, cols = len(grid), len(grid[0])
    table = [[0] * (cols + 1) for _ in range(rows + 1)]
    for r in range(rows):
        for c in range(cols):
            above = table[r][c + 1]
            left = table[r + 1][c]
            corner = table[r][c]
            table[r + 1][c + 1] = grid[r][c] + above + left - corner
    return table

def block_sum(t, r1, c1, r2, c2):
    return t[r2][c2] - t[r1][c2] - t[r2][c1] + t[r1][c1]

if __name__ == "__main__":
    t = prefix_table([[1, 2], [3, 4]])
    assert t[2][2] == 10
    assert block_sum(t, 1, 0, 2, 2) == 7
    assert block_sum(t, 0, 1, 2, 2) == 6
'''
    },
    "P0705": {
        "domain": "Data Aggregation and Statistics",
        "task": "Total sales per region and quarter, then each region's best quarter",
        "category": "Nested loop only",
        "code": '''def best_quarter(sales: dict) -> dict:
    totals = {}
    for region, quarters in sales.items():
        for quarter, amounts in quarters.items():
            totals[(region, quarter)] = sum(amounts)
    best = {}
    for (region, quarter), total in sorted(totals.items()):
        if total > best.get(region, (None, -1))[1]:
            best[region] = (quarter, total)
    return best


if __name__ == "__main__":
    sales = {"n": {"q1": [1, 2], "q2": [5]}, "s": {"q1": [4]}}
    assert best_quarter(sales) == {"n": ("q2", 5), "s": ("q1", 4)}
'''
    },
    "P0706": {
        "domain": "Inventory and Record Management",
        "task": "Explode a bill of materials into raw part quantities",
        "category": "Nested loop only",
        "code": '''def expand_bom(bom, product, quantity):
    needed = {}
    stack = [(product, quantity)]
    while stack:
        item, qty = stack.pop()
        parts = bom.get(item)
        if not parts:
            needed[item] = needed.get(item, 0) + qty
            continue
        for part, per_unit in parts:
            stack.append((part, qty * per_unit))
    return needed

if __name__ == "__main__":
    bom = {"bike": [("wheel", 2), ("frame", 1)]}
    bom["wheel"] = [("spoke", 32), ("rim", 1)]
    needed = expand_bom(bom, "bike", 1)
    assert needed == {"frame": 1, "rim": 2, "spoke": 64}
'''
    },
    "P0707": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Text Gantt chart rows showing the hours each task occupies",
        "category": "Nested loop only",
        "code": '''def gantt_rows(tasks, horizon):
    rows = []
    for name, start, length in tasks:
        cells = []
        for hour in range(horizon):
            cells.append("#" if start <= hour < start + length else ".")
        bar = "".join(cells)
        rows.append(f"{name:<6}{bar}")
    return rows

if __name__ == "__main__":
    rows = gantt_rows([("cut", 1, 2), ("sew", 2, 3)], 6)
    assert rows == ["cut   .##...", "sew   ..###."]
'''
    },

    # 2. COMPLEX CONDITIONAL ONLY (7 programs: P0708 - P0714)
    "P0708": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate a CSS-style hex colour token such as #fa0 or #ffaa00",
        "category": "Complex conditional only",
        "code": '''def is_hex_colour(token):
    body = token[1:]
    hex_digits = set("0123456789abcdefABCDEF")
    if token.startswith("#") and len(body) in (3, 6) and set(body) <= hex_digits:
        return True
    return False

if __name__ == "__main__":
    assert is_hex_colour("#fa0")
    assert is_hex_colour("#FFAA00")
    assert not is_hex_colour("#ffaa0")
    assert not is_hex_colour("ffaa00")
    assert not is_hex_colour("#ggg")
'''
    },
    "P0709": {
        "domain": "Searching and Sorting",
        "task": "Binary search for a value in a rotated sorted list",
        "category": "Complex conditional only",
        "code": '''def find_in_rotated(values, target):
    lo, hi = 0, len(values) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if values[mid] == target:
            return mid
        if values[lo] <= values[mid] and values[lo] <= target < values[mid]:
            hi = mid - 1
        elif values[lo] > values[mid] and values[mid] < target <= values[hi]:
            lo = mid + 1
        elif values[lo] <= values[mid]:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1

if __name__ == "__main__":
    rotated = [4, 5, 6, 7, 0, 1, 2]
    assert find_in_rotated(rotated, 0) == 4
    assert find_in_rotated(rotated, 5) == 1
    assert find_in_rotated(rotated, 3) == -1
'''
    },
    "P0710": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Fill blank fields of a primary contact from a secondary record",
        "category": "Complex conditional only",
        "code": '''def merge_contact(primary: dict, secondary: dict) -> dict:
    merged = dict(primary)
    for field, value in secondary.items():
        current = merged.get(field)
        if current is None or current == "" or isinstance(current, list) and not current:
            merged[field] = value
    return merged


if __name__ == "__main__":
    primary = {"name": "Ann", "phone": "", "tags": []}
    secondary = {"name": "A", "phone": "123", "tags": ["vip"]}
    secondary["email"] = "a@x.org"
    merged = merge_contact(primary, secondary)
    assert merged["name"] == "Ann"
    assert merged["phone"] == "123"
    assert merged["tags"] == ["vip"]
    assert merged["email"] == "a@x.org"
'''
    },
    "P0711": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Whether a room can be booked for a slot given clashes and limits",
        "category": "Complex conditional only",
        "code": '''def can_book(room, start, end, attendees, bookings):
    busy = [b for b in bookings if b[0] < end and start < b[1]]
    if not busy and attendees <= room["capacity"] and end - start <= room["max_hours"]:
        return True
    return False

if __name__ == "__main__":
    room = {"capacity": 8, "max_hours": 2}
    bookings = [(9, 10), (13, 14)]
    assert can_book(room, 10, 12, 6, bookings)
    assert not can_book(room, 9, 11, 6, bookings)
    assert not can_book(room, 10, 12, 9, bookings)
    assert not can_book(room, 15, 18, 2, bookings)
'''
    },
    "P0712": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Rebound heights of a dropped ball and the total distance travelled",
        "category": "Complex conditional only",
        "code": '''def bounce_heights(drop_height, restitution, min_height=0.1, max_bounces=20):
    heights = []
    height = drop_height
    while height >= min_height and len(heights) < max_bounces and restitution < 1:
        height = round(height * restitution, 4)
        heights.append(height)
    distance = drop_height + 2 * sum(heights)
    return heights, round(distance, 4)

if __name__ == "__main__":
    heights, distance = bounce_heights(1.0, 0.5, 0.2)
    assert heights == [0.5, 0.25, 0.125]
    assert distance == 2.75
    assert bounce_heights(1.0, 1.0) == ([], 1.0)
'''
    },
    "P0713": {
        "domain": "Data Aggregation and Statistics",
        "task": "Decide whether a sample with gaps is usable for analysis",
        "category": "Complex conditional only",
        "code": '''def usable_sample(values, max_missing_share=0.1, min_size=5):
    present = [v for v in values if v is not None]
    missing = 1 - len(present) / len(values) if values else 1.0
    spread = max(present) - min(present) if present else 0
    if len(present) >= min_size and missing <= max_missing_share and spread > 0:
        return True
    return False

if __name__ == "__main__":
    assert usable_sample([1, 2, 3, 4, 5])
    assert not usable_sample([1, 2, 3, 4, None])
    assert not usable_sample([3, 3, 3, 3, 3])
    assert not usable_sample([])
'''
    },
    "P0714": {
        "domain": "Inventory and Record Management",
        "task": "Cycle-count frequency for an item from value, age of count and errors",
        "category": "Complex conditional only",
        "code": '''def count_frequency(annual_value: float, last_count_days: int, discrepancies: int) -> str:
    if annual_value >= 10000 or discrepancies >= 3:
        return "monthly"
    elif annual_value >= 1000 and last_count_days > 60 or discrepancies > 0:
        return "quarterly"
    return "yearly"


if __name__ == "__main__":
    assert count_frequency(20000, 10, 0) == "monthly"
    assert count_frequency(5000, 90, 0) == "quarterly"
    assert count_frequency(5000, 10, 1) == "quarterly"
    assert count_frequency(500, 400, 0) == "yearly"
'''
    },

    # 3. LONG STATEMENT AND NESTED LOOP (7 programs: P0715 - P0721)
    "P0715": {
        "domain": "Numerical Computation",
        "task": "Multiply polynomials and estimate a derivative with a five-point stencil",
        "category": "Long statement and nested loop",
        "code": '''def poly_multiply(a, b):
    result = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            result[i + j] += x * y
    return result

def poly_at(coeffs, x):
    total = 0
    for power, c in enumerate(coeffs):
        total += c * x ** power
    return total

def slope_at(c, x, h=1e-3):
    slope = (8 * poly_at(c, x + h) - 8 * poly_at(c, x - h) - poly_at(c, x + 2 * h) + poly_at(c, x - 2 * h)) / (12 * h)
    return slope

if __name__ == "__main__":
    assert poly_multiply([1, 1], [1, -1]) == [1, 0, -1]
    assert abs(slope_at([0, 0, 1], 3.0) - 6.0) < 1e-6
'''
    },
    "P0716": {
        "domain": "Searching and Sorting",
        "task": "Order words by length then alphabetically using length buckets",
        "category": "Long statement and nested loop",
        "code": '''def sort_by_length(words):
    buckets = {}
    for word in words:
        buckets.setdefault(len(word), []).append(word)
    ordered = []
    for length in sorted(buckets):
        for word in sorted(buckets[length]):
            ordered.append(word)
    return ordered

def length_report(words):
    ordered = sort_by_length(words)
    return {"shortest": ordered[0], "longest": ordered[-1], "count": len(ordered)} if ordered else {}

if __name__ == "__main__":
    words = ["pear", "fig", "apple", "kiwi"]
    assert sort_by_length(words) == ["fig", "kiwi", "pear", "apple"]
    assert length_report(words)["longest"] == "apple"
    assert length_report([]) == {}
'''
    },
    "P0717": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Item pair co-occurrence counts across baskets and their lift",
        "category": "Long statement and nested loop",
        "code": '''from itertools import combinations


def co_occurrence(baskets):
    pairs = {}
    for basket in baskets:
        for a, b in combinations(sorted(set(basket)), 2):
            pairs[(a, b)] = pairs.get((a, b), 0) + 1
    return pairs


def pair_lift(pairs, baskets, a, b):
    n = len(baskets)
    count_a = sum(a in basket for basket in baskets)
    count_b = sum(b in basket for basket in baskets)
    ratio = pairs.get((min(a, b), max(a, b)), 0) * n / max(count_a * count_b, 1)
    return round(ratio, 3)


if __name__ == "__main__":
    baskets = [["milk", "bread"], ["milk", "eggs"]]
    baskets.append(["bread", "milk"])
    baskets.append(["eggs"])
    pairs = co_occurrence(baskets)
    assert pairs == {("bread", "milk"): 2, ("eggs", "milk"): 1}
    assert pair_lift(pairs, baskets, "milk", "bread") == 1.333
    assert pair_lift(pairs, baskets, "eggs", "milk") == 0.667
'''
    },
    "P0718": {
        "domain": "Graph or Tree Traversal",
        "task": "Depth-weighted node scores summed level by level in a tree",
        "category": "Long statement and nested loop",
        "code": '''def level_scores(children, weights, root, bonus=0.5):
    totals = []
    level = [root]
    depth = 0
    while level:
        level_total = 0.0
        nxt = []
        for node in level:
            score = weights.get(node, 0) * (depth + 1) + bonus * len(children.get(node, []))
            level_total += score
            nxt.extend(children.get(node, []))
        totals.append(level_total)
        level = nxt
        depth += 1
    return totals

if __name__ == "__main__":
    children = {"r": ["a", "b"], "a": ["c"]}
    weights = {"r": 1, "a": 2, "b": 3, "c": 4}
    assert level_scores(children, weights, "r") == [2.0, 10.5, 12.0]
'''
    },
    "P0719": {
        "domain": "Matrix & Grid Operations",
        "task": "Valid-mode convolution of a grid with a 2x2 kernel",
        "category": "Long statement and nested loop",
        "code": '''def convolve_2x2(grid, k):
    out = []
    for r in range(len(grid) - 1):
        row = []
        for c in range(len(grid[0]) - 1):
            value = grid[r][c] * k[0][0] + grid[r][c + 1] * k[0][1] + grid[r + 1][c] * k[1][0] + grid[r + 1][c + 1] * k[1][1]
            row.append(value)
        out.append(row)
    return out

if __name__ == "__main__":
    grid = [[1, 2, 3], [4, 5, 6]]
    assert convolve_2x2(grid, [[1, 0], [0, -1]]) == [[-4, -4]]
    assert convolve_2x2(grid, [[1, 1], [1, 1]]) == [[12, 16]]
'''
    },
    "P0720": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Minute-by-minute ticket counter queue with several servers",
        "category": "Long statement and nested loop",
        "code": '''def counter_queue(arrivals, servers, service_minutes):
    busy = [0] * servers
    waiting = 0
    log = []
    for minute, arriving in enumerate(arrivals):
        waiting += arriving
        for s in range(servers):
            if busy[s] > 0:
                busy[s] -= 1
            if busy[s] == 0 and waiting > 0:
                busy[s] = service_minutes
                waiting -= 1
        log.append({"minute": minute, "waiting": waiting, "busy": sum(1 for b in busy if b)})
    return log

if __name__ == "__main__":
    log = counter_queue([2, 0, 0, 1], 1, 2)
    assert [entry["waiting"] for entry in log] == [1, 1, 0, 1]
    assert all(entry["busy"] == 1 for entry in log)
'''
    },
    "P0721": {
        "domain": "Inventory and Record Management",
        "task": "Carrying cost of aged stock lots per warehouse with an old-stock surcharge",
        "category": "Long statement and nested loop",
        "code": '''def stock_age_value(warehouses: dict, today: int, holding_rate: float = 0.002) -> dict:
    report = {}
    for site, lots in warehouses.items():
        cost = 0.0
        for qty, unit_cost, received_day in lots:
            age = today - received_day
            carrying = qty * unit_cost * holding_rate * age + qty * unit_cost * (age > 180) * 0.1
            cost += carrying
        report[site] = round(cost, 2)
    return report


if __name__ == "__main__":
    lots = {"w1": [(10, 5.0, 190)], "w2": [(1, 100.0, 0)]}
    assert stock_age_value(lots, 200) == {"w1": 1.0, "w2": 50.0}
'''
    },

    # 4. ALL THREE TARGET ISSUES (7 programs: P0722 - P0728)
    "P0722": {
        "domain": "String Processing & Text Analysis",
        "task": "Keyword hits with a short context snippet, skipping comment lines",
        "category": "All three target issues",
        "code": '''def keyword_hits(lines, keywords, max_hits=10):
    hits = []
    for number, line in enumerate(lines, start=1):
        lowered = line.lower()
        for word in keywords:
            pos = lowered.find(word)
            if pos >= 0 and len(hits) < max_hits and not lowered.startswith("#"):
                snippet = line[max(pos - 5, 0):pos + len(word) + 5].strip() + " @" + str(number)
                hits.append(snippet)
    return hits

if __name__ == "__main__":
    lines = ["Error at disk", "# error ignored", "all good"]
    assert keyword_hits(lines, ["error"]) == ["Error at d @1"]
    assert keyword_hits(lines, ["good"], 0) == []
'''
    },
    "P0723": {
        "domain": "Graph or Tree Traversal",
        "task": "Shortest walkable grid distance and its ratio to the Manhattan distance",
        "category": "All three target issues",
        "code": '''from collections import deque

def grid_distance(grid, start, goal, max_steps):
    rows, cols = len(grid), len(grid[0])
    seen = {start: 0}
    queue = deque([start])
    while queue and goal not in seen:
        r, c = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in seen:
                seen[(nr, nc)] = seen[(r, c)] + 1
                queue.append((nr, nc))
    if goal not in seen or seen[goal] > max_steps:
        return None, 0.0
    manhattan = abs(goal[0] - start[0]) + abs(goal[1] - start[1])
    return seen[goal], round(manhattan / max(seen[goal], 1), 3)

if __name__ == "__main__":
    grid = ["..#", "...", "#.."]
    assert grid_distance(grid, (0, 0), (2, 2), 10) == (4, 1.0)
    assert grid_distance(grid, (0, 0), (2, 2), 3) == (None, 0.0)
    assert grid_distance([".#", "#."], (0, 0), (1, 1), 9) == (None, 0.0)
'''
    },
    "P0724": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Place meetings into the smallest free room that fits, reporting drops",
        "category": "All three target issues",
        "code": '''def allocate_rooms(meetings, rooms):
    free_at = {name: 0 for name, _ in rooms}
    placed, dropped = {}, []
    for title, start, end, size in sorted(meetings, key=lambda m: (m[1], -m[3])):
        chosen, chosen_cap = None, float("inf")
        for name, capacity in rooms:
            if free_at[name] <= start and capacity >= size and capacity < chosen_cap:
                chosen, chosen_cap = name, capacity
        if chosen is None:
            dropped.append(title)
            continue
        free_at[chosen] = end
        placed[title] = chosen
    return placed, dropped, round(len(placed) / max(len(meetings), 1) * 100, 1)

if __name__ == "__main__":
    rooms = [("small", 4), ("big", 10)]
    meetings = [("standup", 9, 10, 3), ("allhands", 9, 11, 8)]
    meetings.append(("sync", 10, 11, 4))
    meetings.append(("review", 9, 10, 9))
    placed, dropped, rate = allocate_rooms(meetings, rooms)
    assert placed == {"review": "big", "standup": "small", "sync": "small"}
    assert dropped == ["allhands"]
    assert rate == 75.0
'''
    },
    "P0725": {
        "domain": "Matrix & Grid Operations",
        "task": "Rank of a matrix by Gaussian elimination with partial pivoting",
        "category": "All three target issues",
        "code": '''def matrix_rank(matrix, eps=1e-9):
    m = [list(map(float, row)) for row in matrix]
    rank = 0
    rows, cols = len(m), len(m[0])
    for col in range(cols):
        pivot = None
        for r in range(rank, rows):
            if abs(m[r][col]) > eps and (pivot is None or abs(m[r][col]) > abs(m[pivot][col])):
                pivot = r
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        for r in range(rows):
            if r != rank:
                factor = m[r][col] / m[rank][col] if abs(m[rank][col]) > eps else 0.0
                m[r] = [a - factor * b for a, b in zip(m[r], m[rank])]
        rank += 1
    return rank

if __name__ == "__main__":
    assert matrix_rank([[1, 2], [2, 4]]) == 1
    assert matrix_rank([[1, 0], [0, 1]]) == 2
    assert matrix_rank([[0, 0], [0, 0]]) == 0
    assert matrix_rank([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == 2
'''
    },
    "P0726": {
        "domain": "Data Aggregation and Statistics",
        "task": "Per-category mean with a finite-population margin, keeping stable groups",
        "category": "All three target issues",
        "code": '''def category_summary(rows, min_count=2, max_cv=0.5, population=100):
    groups = {}
    for category, value in rows:
        groups.setdefault(category, []).append(value)
    summary = {}
    for category, values in sorted(groups.items()):
        n = len(values)
        mean = sum(values) / n
        sq = 0.0
        for v in values:
            sq += (v - mean) ** 2
        std = (sq / n) ** 0.5
        cv = std / mean if mean else float("inf")
        margin = 1.96 * std / n ** 0.5 * ((population - n) / max(population - 1, 1)) ** 0.5
        if n >= min_count and cv <= max_cv and mean > 0:
            summary[category] = (n, round(mean, 2), round(margin, 2))
    return summary

if __name__ == "__main__":
    rows = [("a", 10), ("a", 12), ("b", 5)]
    rows.extend([("c", 1), ("c", 100)])
    assert category_summary(rows) == {"a": (2, 11.0, 1.38)}
'''
    },
    "P0727": {
        "domain": "Numerical Computation",
        "task": "Bounded integer solutions of ax + by = c with even sum and x <= y",
        "category": "All three target issues",
        "code": '''def bounded_solutions(a: int, b: int, c: int, low: int, high: int) -> tuple:
    found = []
    for x in range(low, high + 1):
        for y in range(low, high + 1):
            if a * x + b * y == c and x <= y and (x + y) % 2 == 0:
                found.append((x, y))
    return found, min(found, key=lambda p: abs(p[0]) + abs(p[1])) if found else None


if __name__ == "__main__":
    found, smallest = bounded_solutions(1, 1, 4, -5, 5)
    assert found == [(-1, 5), (0, 4), (1, 3), (2, 2)]
    assert smallest == (0, 4)
    assert bounded_solutions(2, 2, 3, -5, 5) == ([], None)
'''
    },
    "P0728": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Deterministic ring-road traffic automaton and mean speed per step",
        "category": "All three target issues",
        "code": '''def traffic_step(road, vmax=3):
    length = len(road)
    new_road = [-1] * length
    for pos in range(length):
        speed = road[pos]
        if speed < 0:
            continue
        gap = 0
        while gap < vmax and road[(pos + gap + 1) % length] < 0 and gap < length - 1:
            gap += 1
        new_speed = min(speed + 1, vmax, gap)
        new_road[(pos + new_speed) % length] = new_speed
    return new_road

def run_traffic(road, steps, vmax=3):
    flows = []
    for _ in range(steps):
        road = traffic_step(road, vmax)
        flows.append(sum(v for v in road if v >= 0) / max(sum(1 for v in road if v >= 0), 1))
    return road, flows

if __name__ == "__main__":
    road = [0, -1, -1, 0, -1, -1]
    final, flows = run_traffic(road, 2, 2)
    assert final == [2, -1, -1, 2, -1, -1]
    assert flows == [1.0, 2.0]
'''
    },

    # 5. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0729 - P0734)
    "P0729": {
        "domain": "Searching and Sorting",
        "task": "Index pairs within a distance whose distinct values sum into a range",
        "category": "Nested loop and complex conditional",
        "code": '''def window_pairs(values, low, high, max_distance):
    pairs = []
    for i in range(len(values)):
        for j in range(i + 1, min(i + max_distance + 1, len(values))):
            total = values[i] + values[j]
            if low <= total <= high and values[i] != values[j]:
                pairs.append((i, j))
    return pairs

if __name__ == "__main__":
    assert window_pairs([1, 4, 2, 3], 4, 5, 2) == [(0, 1), (2, 3)]
    assert window_pairs([2, 2], 4, 4, 1) == []
'''
    },
    "P0730": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Fields where duplicate-key records disagree with the first record",
        "category": "Nested loop and complex conditional",
        "code": '''def conflicting_records(records: list[dict], key_field: str) -> list[tuple]:
    conflicts = []
    first_seen = {}
    for record in records:
        key = record[key_field]
        if key not in first_seen:
            first_seen[key] = record
            continue
        original = first_seen[key]
        for field, value in record.items():
            if field != key_field and field in original and original[field] != value:
                conflicts.append((key, field))
    return conflicts


if __name__ == "__main__":
    records = [{"id": 1, "name": "a", "age": 3}]
    records.append({"id": 1, "name": "b", "age": 3})
    records.append({"id": 2, "name": "c"})
    assert conflicting_records(records, "id") == [(1, "name")]
'''
    },
    "P0731": {
        "domain": "Graph or Tree Traversal",
        "task": "Known nodes reachable within k hops while avoiding blocked nodes",
        "category": "Nested loop and complex conditional",
        "code": '''def within_hops(graph, start, k, blocked):
    frontier = [start]
    seen = {start}
    for _ in range(k):
        nxt = []
        for node in frontier:
            for nbr in graph.get(node, []):
                if nbr not in seen and nbr not in blocked and nbr in graph:
                    seen.add(nbr)
                    nxt.append(nbr)
        frontier = nxt
    return sorted(seen - {start})

if __name__ == "__main__":
    graph = {"a": ["b", "c"], "b": ["d"], "c": ["d", "x"]}
    graph["d"] = ["e"]
    graph["e"] = []
    assert within_hops(graph, "a", 2, {"c"}) == ["b", "d"]
    assert within_hops(graph, "a", 3, set()) == ["b", "c", "d", "e"]
'''
    },
    "P0732": {
        "domain": "Matrix & Grid Operations",
        "task": "Free seats in a seat map whose left and right neighbours are also free",
        "category": "Nested loop and complex conditional",
        "code": '''def distanced_seats(seats):
    good = []
    for r, row in enumerate(seats):
        for c, seat in enumerate(row):
            left_free = c == 0 or row[c - 1] == "."
            right_free = c == len(row) - 1 or row[c + 1] == "."
            if seat == "." and left_free and right_free:
                good.append((r, c))
    return good

if __name__ == "__main__":
    seats = ["..X.", "...."]
    expected = [(0, 0), (1, 0), (1, 1), (1, 2), (1, 3)]
    assert distanced_seats(seats) == expected
'''
    },
    "P0733": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Round-robin rock-paper-scissors tournament points from move strings",
        "category": "Nested loop and complex conditional",
        "code": '''def rps_table(strategies):
    beats = {"R": "S", "S": "P", "P": "R"}
    points = {name: 0 for name in strategies}
    names = sorted(strategies)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            for move_a, move_b in zip(strategies[a], strategies[b]):
                if move_a != move_b and move_a in beats and beats[move_a] == move_b:
                    points[a] += 1
                elif move_a != move_b and move_b in beats and beats[move_b] == move_a:
                    points[b] += 1
    return points

if __name__ == "__main__":
    strategies = {"ann": "RRP", "bob": "SPP", "cy": "RRR"}
    assert rps_table(strategies) == {"ann": 2, "bob": 3, "cy": 1}
'''
    },
    "P0734": {
        "domain": "String Processing & Text Analysis",
        "task": "Dictionary words exactly one insert, delete or substitution away",
        "category": "Nested loop and complex conditional",
        "code": '''def near_matches(word, dictionary):
    matches = []
    for candidate in dictionary:
        if abs(len(candidate) - len(word)) > 1:
            continue
        i = j = edits = 0
        while i < len(word) and j < len(candidate) and edits <= 1:
            if word[i] == candidate[j]:
                i += 1
                j += 1
                continue
            edits += 1
            if len(word) > len(candidate):
                i += 1
            elif len(candidate) > len(word):
                j += 1
            else:
                i += 1
                j += 1
        if edits + len(word) - i + len(candidate) - j == 1:
            matches.append(candidate)
    return matches

if __name__ == "__main__":
    words = ["cat", "cot", "cast", "at", "dog", "cats"]
    assert near_matches("cat", words) == ["cot", "cast", "at", "cats"]
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0735 - P0740)
    "P0735": {
        "domain": "Searching and Sorting",
        "task": "Pick insertion, merge or heap sort from size, disorder and constraints",
        "category": "Long statement and complex conditional",
        "code": '''import math

def choose_sort(n, inversions, memory_limited, stable_needed, memory_penalty=0.5):
    log_n = math.log2(max(n, 2))
    insertion_cost = n + inversions
    merge_cost = n * log_n * 1.2 + memory_penalty * n * memory_limited
    heap_cost = n * log_n * 2.0
    if insertion_cost < merge_cost and n <= 5000 or inversions == 0:
        return "insertion", insertion_cost
    if stable_needed or not memory_limited:
        return "merge", round(merge_cost, 1)
    return "heap", round(heap_cost, 1)

if __name__ == "__main__":
    assert choose_sort(100, 0, False, False) == ("insertion", 100)
    assert choose_sort(10000, 10 ** 7, False, True)[0] == "merge"
    assert choose_sort(10000, 10 ** 7, True, False)[0] == "heap"
'''
    },
    "P0736": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Drop contacts whose email or phone digits were already seen",
        "category": "Long statement and complex conditional",
        "code": '''def dedupe_contacts(contacts):
    seen_emails, seen_phones = set(), set()
    kept = []
    for c in contacts:
        email = c.get("email", "").strip().lower()
        raw = c.get("phone", "")
        phone = "".join(ch for ch in raw if ch.isdigit())
        if email in seen_emails and email or phone in seen_phones and phone:
            continue
        seen_emails.add(email)
        seen_phones.add(phone)
        kept.append(c)
    return kept, len(contacts) - len(kept), round(len(kept) / max(len(contacts), 1), 2)

if __name__ == "__main__":
    contacts = [{"email": "A@x.com", "phone": "12-3"}]
    contacts.append({"email": "a@x.com"})
    contacts.append({"phone": "123"})
    contacts.append({"email": "b@x.com", "phone": "999"})
    kept, removed, share = dedupe_contacts(contacts)
    assert [c.get("phone") for c in kept] == ["12-3", "999"]
    assert (removed, share) == (2, 0.5)
'''
    },
    "P0737": {
        "domain": "Inventory and Record Management",
        "task": "Reorder urgency from projected stock after lead time and safety days",
        "category": "Long statement and complex conditional",
        "code": '''def reorder_urgency(on_hand, daily_demand, lead_time_days, safety_days=3, on_order=0):
    projected = on_hand + on_order - daily_demand * lead_time_days - daily_demand * safety_days
    if projected < 0 and on_order == 0 or on_hand < daily_demand:
        return "urgent", projected
    if projected < daily_demand * 7:
        return "soon", projected
    return "ok", projected

if __name__ == "__main__":
    assert reorder_urgency(10, 5, 4) == ("urgent", -25)
    assert reorder_urgency(100, 5, 4) == ("ok", 65)
    assert reorder_urgency(50, 5, 4) == ("soon", 15)
    assert reorder_urgency(40, 5, 4, on_order=50) == ("ok", 55)
'''
    },
    "P0738": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Weekly pay with premium rates for weekends, long days and overtime",
        "category": "Long statement and complex conditional",
        "code": '''def weekly_pay(hours_by_day, rate, weekend_days=("sat", "sun")):
    pay = 0.0
    total_hours = 0
    for day, hours in hours_by_day.items():
        total_hours += hours
        weekend = day in weekend_days
        if weekend and hours > 0 or hours > 10 or total_hours > 40:
            pay += hours * rate * 1.5 + (hours - 8) * rate * 0.25 * (hours > 8)
        else:
            pay += hours * rate
    return round(pay, 2)

if __name__ == "__main__":
    assert weekly_pay({"mon": 8, "sat": 4}, 10) == 140.0
    assert weekly_pay({"mon": 12}, 10) == 190.0
'''
    },
    "P0739": {
        "domain": "Numerical Computation",
        "task": "Numerically stable real roots of a quadratic equation",
        "category": "Long statement and complex conditional",
        "code": '''import math


def stable_quadratic_roots(a: float, b: float, c: float):
    disc = b * b - 4 * a * c
    if a == 0 or disc < 0 or math.isnan(disc):
        return None
    q = -0.5 * (b + math.copysign(math.sqrt(disc), b))
    return (min(q / a, c / q), max(q / a, c / q)) if q != 0 else (0.0, 0.0)


if __name__ == "__main__":
    assert stable_quadratic_roots(1, -3, 2) == (1.0, 2.0)
    assert stable_quadratic_roots(1, 0, 1) is None
    assert stable_quadratic_roots(0, 1, 1) is None
    assert stable_quadratic_roots(1, 0, 0) == (0.0, 0.0)
    small = stable_quadratic_roots(1, 1e8, 1)[1]
    assert abs(small + 1e-8) < 1e-12
'''
    },
    "P0740": {
        "domain": "Data Aggregation and Statistics",
        "task": "Label a series rising, falling or flat from its least-squares slope",
        "category": "Long statement and complex conditional",
        "code": '''def trend_label(values, flat_band=0.05):
    n = len(values)
    if n < 2:
        return "flat", 0.0
    xs = range(n)
    mean_x = (n - 1) / 2
    mean_y = sum(values) / n
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, values)) / sum((x - mean_x) ** 2 for x in xs)
    relative = slope / abs(mean_y) if mean_y else slope
    if relative > flat_band and values[-1] > values[0] or relative > 3 * flat_band:
        return "rising", round(slope, 3)
    if relative < -flat_band:
        return "falling", round(slope, 3)
    return "flat", round(slope, 3)

if __name__ == "__main__":
    assert trend_label([1, 2, 3, 4]) == ("rising", 1.0)
    assert trend_label([4, 3, 2, 1]) == ("falling", -1.0)
    assert trend_label([5, 5, 5]) == ("flat", 0.0)
    assert trend_label([1]) == ("flat", 0.0)
'''
    },

    # 7. NONE (5 programs: P0741 - P0745)
    "P0741": {
        "domain": "Numerical Computation",
        "task": "Convert integers to any base up to 36 and back",
        "category": "None",
        "code": '''DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def to_base(n: int, base: int) -> str:
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    out = []
    while n:
        n, r = divmod(n, base)
        out.append(DIGITS[r])
    return sign + "".join(reversed(out))


def from_base(text: str, base: int) -> int:
    return int(text, base)


if __name__ == "__main__":
    assert to_base(255, 16) == "ff"
    assert to_base(-10, 2) == "-1010"
    assert from_base("zz", 36) == 1295
    assert from_base(to_base(987654, 7), 7) == 987654
'''
    },
    "P0742": {
        "domain": "String Processing & Text Analysis",
        "task": "Numeronym abbreviations such as i18n for long words and a reverse check",
        "category": "None",
        "code": '''def numeronym(word, min_length=5):
    if len(word) < min_length:
        return word
    return f"{word[0]}{len(word) - 2}{word[-1]}"

def numeronym_sentence(text):
    return " ".join(numeronym(w) for w in text.split())

def matches_numeronym(short, full):
    count = int(short[1:-1])
    return len(full) == count + 2 and full[0] == short[0]

if __name__ == "__main__":
    assert numeronym("internationalization") == "i18n"
    assert numeronym_sentence("localization is fun") == "l10n is fun"
    assert matches_numeronym("i18n", "internationalization")
    assert not matches_numeronym("k9s", "kubernetes")
'''
    },
    "P0743": {
        "domain": "Searching and Sorting",
        "task": "Smallest ship capacity that moves ordered parcels within a day limit",
        "category": "None",
        "code": '''def days_needed(weights, capacity):
    days, load = 1, 0
    for w in weights:
        if load + w > capacity:
            days += 1
            load = 0
        load += w
    return days

def min_ship_capacity(weights, days):
    lo, hi = max(weights), sum(weights)
    while lo < hi:
        mid = (lo + hi) // 2
        if days_needed(weights, mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo

if __name__ == "__main__":
    assert min_ship_capacity(list(range(1, 11)), 5) == 15
    assert min_ship_capacity([3, 2, 2, 4, 1, 4], 3) == 6
'''
    },
    "P0744": {
        "domain": "Graph or Tree Traversal",
        "task": "Lowest common ancestor of two nodes from a child-to-parent map",
        "category": "None",
        "code": '''def ancestors(parent: dict, node) -> list:
    chain = [node]
    while node in parent:
        node = parent[node]
        chain.append(node)
    return chain


def shared_ancestor(parent: dict, a, b):
    seen = set(ancestors(parent, a))
    for node in ancestors(parent, b):
        if node in seen:
            return node
    return None


if __name__ == "__main__":
    parent = {"b": "a", "c": "a", "d": "b", "e": "b"}
    assert shared_ancestor(parent, "d", "e") == "b"
    assert shared_ancestor(parent, "d", "c") == "a"
    assert shared_ancestor(parent, "d", "z") is None
'''
    },
    "P0745": {
        "domain": "Matrix & Grid Operations",
        "task": "Mirror and invert a binary image, count set pixels and crop a window",
        "category": "None",
        "code": '''def flip_and_invert(image):
    return [[1 - p for p in reversed(row)] for row in image]

def count_ones(image):
    return sum(map(sum, image))

def crop(image, top, left, h, w):
    rows = image[top:top + h]
    return [row[left:left + w] for row in rows]

if __name__ == "__main__":
    img = [[1, 0, 0], [1, 0, 1]]
    assert flip_and_invert(img) == [[1, 1, 0], [0, 1, 0]]
    assert count_ones(img) == 3
    assert crop(img, 0, 1, 2, 2) == [[0, 0], [0, 1]]
'''
    },

    # 8. LONG STATEMENT ONLY (5 programs: P0746 - P0750)
    "P0746": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Cart total with volume discount, coupon and small-order shipping",
        "category": "Long statement only",
        "code": '''def cart_summary(cart: list[tuple[str, int, float]], coupon: float = 0.0) -> tuple:
    subtotal = sum(qty * price for _, qty, price in cart)
    units = sum(qty for _, qty, _ in cart)
    total = subtotal - subtotal * min(units // 10 * 0.05, 0.2) - coupon + 4.99 * (subtotal < 50)
    return round(total, 2), units


if __name__ == "__main__":
    cart = [("pen", 10, 1.0), ("pad", 2, 5.0)]
    assert cart_summary(cart) == (23.99, 12)
    assert cart_summary([("tv", 1, 100.0)], 10) == (90.0, 1)
'''
    },
    "P0747": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Critical ratio of each job and the resulting processing order",
        "category": "Long statement only",
        "code": '''def critical_ratios(jobs, today):
    ratios = {}
    for name, due, remaining_hours, hours_per_day in jobs:
        days_of_work = remaining_hours / hours_per_day
        ratios[name] = round((due - today) / days_of_work, 2)
    return sorted(ratios, key=lambda n: (ratios[n], n)), min(ratios.values(), default=None)

if __name__ == "__main__":
    jobs = [("a", 20, 16, 8), ("b", 12, 8, 8), ("c", 15, 40, 8)]
    assert critical_ratios(jobs, 10) == (["c", "b", "a"], 1.0)
    assert critical_ratios([], 10) == ([], None)
'''
    },
    "P0748": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Drone battery energy left after each flight segment",
        "category": "Long statement only",
        "code": '''def flight_battery(segments, capacity_wh=100.0, hover_w=150.0):
    remaining = capacity_wh
    log = []
    for seconds, speed, climb in segments:
        remaining -= (hover_w + 2.5 * speed ** 2 + 30 * max(climb, 0)) * seconds / 3600
        log.append(round(max(remaining, 0.0), 2))
    return log

if __name__ == "__main__":
    assert flight_battery([(3600, 0, 0)]) == [0.0]
    assert flight_battery([(360, 10, 0), (360, 0, 1)]) == [60.0, 42.0]
'''
    },
    "P0749": {
        "domain": "Data Aggregation and Statistics",
        "task": "Plain and adjusted R-squared of fitted values against actuals",
        "category": "Long statement only",
        "code": '''def r_squared(actual, fitted, predictors=1):
    n = len(actual)
    mean = sum(actual) / n
    errors = [a - f for a, f in zip(actual, fitted)]
    residual_sum = sum(e * e for e in errors)
    total_sum = sum((a - mean) ** 2 for a in actual)
    if not total_sum or n <= predictors + 1:
        return 0.0, 0.0
    plain = 1 - residual_sum / total_sum
    adjusted = 1 - residual_sum / total_sum * (n - 1) / (n - predictors - 1)
    return round(plain, 4), round(adjusted, 4)

if __name__ == "__main__":
    fitted = [1.1, 1.9, 3.2, 3.8]
    assert r_squared([1, 2, 3, 4], fitted) == (0.98, 0.97)
    assert r_squared([1, 2, 3], [1, 2, 3]) == (1.0, 1.0)
    assert r_squared([2, 2, 2], [2, 2, 2]) == (0.0, 0.0)
'''
    },
    "P0750": {
        "domain": "Inventory and Record Management",
        "task": "Warehouse pick list ordered by bin location with bulk-line tags",
        "category": "Long statement only",
        "code": '''def pick_list(order_lines, locations):
    picks = []
    for sku, qty in sorted(order_lines, key=lambda line: locations.get(line[0], "ZZ")):
        bin_code = locations.get(sku, "UNSLOTTED")
        tag = "BULK" if qty >= 50 else ""
        picks.append(f"{bin_code:<10}{sku:<8}x{qty:>3} {tag}".rstrip())
    return picks

if __name__ == "__main__":
    locations = {"nut": "A01", "bolt": "B07"}
    picks = pick_list([("bolt", 60), ("nut", 5)], locations)
    assert picks[0].split() == ["A01", "nut", "x", "5"]
    assert picks[1].split() == ["B07", "bolt", "x", "60", "BULK"]
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 15",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v15.0-expansion",
        "programs": BATCH15_PROGRAMS,
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