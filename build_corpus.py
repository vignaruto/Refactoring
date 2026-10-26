"""
build_corpus.py
Writes the Batch 12 (P0551-P0600) programs into program_corpus/programs and
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

BATCH12_PROGRAMS = {
    # 1. COMPLEX CONDITIONAL ONLY (17 programs: P0551 - P0567)
    "P0551": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Vending machine that dispenses only with stock and enough credit",
        "category": "Complex conditional only",
        "code": '''class VendingMachine:
    def __init__(self, stock, prices):
        self.stock = stock
        self.prices = prices
        self.credit = 0

    def insert(self, coins):
        self.credit += coins

    def select(self, item):
        price = self.prices.get(item)
        if price is None:
            return "unknown"
        if self.stock.get(item, 0) > 0 and self.credit >= price and price > 0:
            self.stock[item] -= 1
            self.credit -= price
            return "dispensed"
        return "denied"

if __name__ == "__main__":
    vm = VendingMachine({"cola": 1}, {"cola": 150})
    vm.insert(200)
    assert vm.select("cola") == "dispensed"
    assert vm.credit == 50
    assert vm.select("cola") == "denied"
    assert vm.select("tea") == "unknown"
'''
    },
    "P0552": {
        "domain": "Inventory and Record Management",
        "task": "Decide whether two contact records describe the same person",
        "category": "Complex conditional only",
        "code": '''def digits_only(text):
    return "".join(ch for ch in text if ch.isdigit())

def same_contact(a, b):
    mail_a = a.get("email", "").lower()
    mail_b = b.get("email", "").lower()
    if mail_a and mail_a == mail_b:
        return True
    phone_a = digits_only(a.get("phone", ""))
    phone_b = digits_only(b.get("phone", ""))
    if phone_a and phone_a == phone_b and a["last"].lower() == b["last"].lower():
        return True
    return False

if __name__ == "__main__":
    x = {"email": "Ann@x.com", "last": "Lee"}
    y = {"email": "ann@X.com", "last": "Li"}
    assert same_contact(x, y)
    p = {"phone": "(555) 010-2000", "last": "Rao"}
    q = {"phone": "555 010 2000", "last": "rao"}
    assert same_contact(p, q)
    assert not same_contact(p, {"phone": "5550102000", "last": "Roy"})
'''
    },
    "P0553": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Accept an extra delivery stop if shift time and van capacity allow",
        "category": "Complex conditional only",
        "code": '''def accept_extra_stop(route_minutes, stop_minutes, shift_end, now, van_load, parcel, capacity):
    finish = now + route_minutes + stop_minutes
    if finish <= shift_end and van_load + parcel <= capacity and stop_minutes < 45:
        return True
    return False

if __name__ == "__main__":
    assert accept_extra_stop(120, 20, 600, 400, 10, 5, 20)
    assert not accept_extra_stop(120, 20, 600, 400, 30, 5, 20)
    assert not accept_extra_stop(120, 50, 900, 400, 1, 1, 20)
'''
    },
    "P0554": {
        "domain": "String Processing & Text Analysis",
        "task": "Check that text has the shape of an ISO YYYY-MM-DD date",
        "category": "Complex conditional only",
        "code": '''def looks_like_iso_date(text: str) -> bool:
    parts = text.split("-")
    if len(parts) != 3:
        return False
    year, month, day = parts
    ok = year.isdigit() and month.isdigit() and day.isdigit()
    if ok and len(year) == 4 and 1 <= int(month) <= 12 and 1 <= int(day) <= 31:
        return True
    return False

if __name__ == "__main__":
    assert looks_like_iso_date("2024-02-29")
    assert not looks_like_iso_date("2024-13-01")
    assert not looks_like_iso_date("24-01-01")
    assert not looks_like_iso_date("2024-1a-01")
    assert not looks_like_iso_date("2024/01/01")
'''
    },
    "P0555": {
        "domain": "Numerical Computation",
        "task": "Test whether three distinct points lie on one line",
        "category": "Complex conditional only",
        "code": '''def collinear_distinct(p, q, r, tol=1e-9):
    cross_a = (q[0] - p[0]) * (r[1] - p[1])
    cross_b = (q[1] - p[1]) * (r[0] - p[0])
    if abs(cross_a - cross_b) <= tol and p != q and q != r and p != r:
        return True
    return False

if __name__ == "__main__":
    assert collinear_distinct((0, 0), (1, 1), (2, 2))
    assert not collinear_distinct((0, 0), (1, 1), (1, 1))
    assert not collinear_distinct((0, 0), (1, 0), (0, 1))
'''
    },
    "P0556": {
        "domain": "Data Aggregation and Statistics",
        "task": "Index of the first week in a run of consecutive sales declines",
        "category": "Complex conditional only",
        "code": '''def first_decline_streak(sales: list[float], length: int, drop: float) -> int:
    i = 1
    streak = 0
    while i < len(sales) and streak < length and length > 0:
        if sales[i] <= sales[i - 1] - drop:
            streak += 1
        else:
            streak = 0
        i += 1
    return i - length if streak == length else -1

if __name__ == "__main__":
    weekly = [10, 8, 6, 7, 5, 3, 1]
    assert first_decline_streak(weekly, 3, 1) == 4
    assert first_decline_streak([1, 2, 3], 2, 1) == -1
'''
    },
    "P0557": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Resolve a name through an alias table with prefix fallback",
        "category": "Complex conditional only",
        "code": '''def resolve_alias(name, aliases, fallback=None):
    key = name.strip().lower()
    if key in aliases:
        return aliases[key]
    for alias, target in aliases.items():
        if alias.startswith(key) and len(key) >= 3 and target is not None:
            return target
    return fallback

if __name__ == "__main__":
    aliases = {"nyc": "New York", "losangeles": "Los Angeles"}
    assert resolve_alias(" NYC ", aliases) == "New York"
    assert resolve_alias("losan", aliases) == "Los Angeles"
    assert resolve_alias("lo", aliases, "?") == "?"
'''
    },
    "P0558": {
        "domain": "Searching and Sorting",
        "task": "Index of the smallest element in a rotated sorted list",
        "category": "Complex conditional only",
        "code": '''def rotation_point(values):
    lo, hi = 0, len(values) - 1
    while lo < hi and values and values[lo] > values[hi]:
        mid = (lo + hi) // 2
        if values[mid] > values[hi]:
            lo = mid + 1
        else:
            hi = mid
    return lo

if __name__ == "__main__":
    assert rotation_point([4, 5, 6, 1, 2, 3]) == 3
    assert rotation_point([1, 2, 3]) == 0
    assert rotation_point([2, 1]) == 1
    assert rotation_point([]) == 0
'''
    },
    "P0559": {
        "domain": "Inventory and Record Management",
        "task": "List validation problems in a vehicle service record",
        "category": "Complex conditional only",
        "code": '''def service_record_errors(record):
    """Return the names of the fields that fail validation."""
    errors = []
    km = record.get("odometer_km", -1)
    if not record.get("vin") or len(record["vin"]) != 17:
        errors.append("vin")
    if km < 0 or km > 2_000_000 or not isinstance(km, int):
        errors.append("odometer")
    if record.get("next_due_km") is not None and record["next_due_km"] <= km:
        errors.append("next_due")
    return errors

if __name__ == "__main__":
    good = {"vin": "1HGCM82633A004352", "odometer_km": 5000}
    assert service_record_errors(good) == []
    bad = {"vin": "X", "odometer_km": -3, "next_due_km": -10}
    assert service_record_errors(bad) == ["vin", "odometer", "next_due"]
'''
    },
    "P0560": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Garden watering minutes from soil moisture, rain, heat and hour",
        "category": "Complex conditional only",
        "code": '''def watering_minutes(soil_moisture: float, rain_mm: float, temp_c: float, hour: int) -> int:
    if rain_mm > 5:
        return 0
    if soil_moisture < 0.25 and temp_c > 30 and not 11 <= hour <= 16:
        return 20
    if soil_moisture < 0.35 or temp_c > 35:
        return 10
    return 0

if __name__ == "__main__":
    assert watering_minutes(0.2, 0, 32, 7) == 20
    assert watering_minutes(0.2, 0, 32, 12) == 10
    assert watering_minutes(0.5, 0, 20, 7) == 0
    assert watering_minutes(0.1, 9, 40, 7) == 0
'''
    },
    "P0561": {
        "domain": "Scheduling and Resource Allocation",
        "task": "First free charging bay that suits a vehicle's power and speed needs",
        "category": "Complex conditional only",
        "code": '''def pick_charging_bay(bays, needs_fast, vehicle_kw):
    for bay_id, free, max_kw, fast in bays:
        if free and max_kw >= vehicle_kw and (fast or not needs_fast):
            return bay_id
    return None

if __name__ == "__main__":
    bays = [(1, False, 50, True), (2, True, 22, False)]
    bays.append((3, True, 150, True))
    assert pick_charging_bay(bays, False, 11) == 2
    assert pick_charging_bay(bays, True, 50) == 3
    assert pick_charging_bay(bays, True, 200) is None
'''
    },
    "P0562": {
        "domain": "String Processing & Text Analysis",
        "task": "Decide whether a sentence reads as a question",
        "category": "Complex conditional only",
        "code": '''def is_question(sentence: str) -> bool:
    text = sentence.strip()
    if not text:
        return False
    first = text.split()[0].lower().strip(",")
    starters = {"who", "what", "why", "how", "is", "can"}
    if text.endswith("?") or first in starters and len(text.split()) > 2 and not text.endswith("."):
        return True
    return False

if __name__ == "__main__":
    assert is_question("Is it raining")
    assert is_question("ok?")
    assert not is_question("Why.")
    assert not is_question("Can you go.")
    assert not is_question("")
'''
    },
    "P0563": {
        "domain": "Numerical Computation",
        "task": "Convergence test on the last values of an iteration history",
        "category": "Complex conditional only",
        "code": '''def has_converged(history: list[float], abs_tol: float, rel_tol: float) -> bool:
    if len(history) < 3:
        return False
    last, prev, before = history[-1], history[-2], history[-3]
    change = abs(last - prev)
    if change <= abs_tol or change <= rel_tol * abs(last) and abs(prev - before) <= abs_tol * 10:
        return True
    return False

if __name__ == "__main__":
    assert has_converged([1.0, 1.5, 1.5000001], 1e-6, 1e-9)
    assert not has_converged([1.0, 2.0, 3.0], 1e-6, 1e-9)
    assert not has_converged([1.0], 1.0, 1.0)
'''
    },
    "P0564": {
        "domain": "Data Aggregation and Statistics",
        "task": "Customer segment from recency, frequency and monetary value",
        "category": "Complex conditional only",
        "code": '''def rfm_segment(recency_days: int, frequency: int, monetary: float) -> str:
    if recency_days <= 30 and frequency >= 10 and monetary >= 500:
        return "champion"
    if recency_days > 180 and frequency <= 2:
        return "lost"
    if recency_days <= 90 or frequency >= 5 or monetary >= 1000:
        return "loyal"
    return "casual"

if __name__ == "__main__":
    assert rfm_segment(10, 12, 800) == "champion"
    assert rfm_segment(200, 1, 50) == "lost"
    assert rfm_segment(100, 6, 10) == "loyal"
    assert rfm_segment(120, 3, 100) == "casual"
'''
    },
    "P0565": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Keep complete rows matching a column filter up to a limit",
        "category": "Complex conditional only",
        "code": '''def filter_rows(rows: list[tuple], spec: dict[int, object], limit: int) -> list[tuple]:
    kept = []
    for row in rows:
        matches = all(row[i] == v for i, v in spec.items())
        if matches and len(kept) < limit and None not in row:
            kept.append(row)
    return kept

if __name__ == "__main__":
    rows = [(1, "a"), (2, "b"), (1, "b"), (1, None)]
    assert filter_rows(rows, {0: 1}, 5) == [(1, "a"), (1, "b")]
    assert filter_rows(rows, {0: 1}, 1) == [(1, "a")]
'''
    },
    "P0566": {
        "domain": "Graph or Tree Traversal",
        "task": "Recursive check that a binary tree keeps search-tree ordering",
        "category": "Complex conditional only",
        "code": '''def check_search_tree_order(tree, node, low=None, high=None):
    if node is None:
        return True
    value, left, right = tree[node]
    if value is None or low is not None and value <= low or high is not None and value >= high:
        return False
    if not check_search_tree_order(tree, left, low, value):
        return False
    return check_search_tree_order(tree, right, value, high)

if __name__ == "__main__":
    t = {"r": (8, "a", "b"), "a": (3, None, None)}
    t["b"] = (10, "c", None)
    t["c"] = (9, None, None)
    assert check_search_tree_order(t, "r")
    t["c"] = (7, None, None)
    assert not check_search_tree_order(t, "r")
'''
    },
    "P0567": {
        "domain": "Searching and Sorting",
        "task": "Check that an array satisfies the min-heap property",
        "category": "Complex conditional only",
        "code": '''def is_min_heap_array(values):
    n = len(values)
    for i in range(n):
        left, right = 2 * i + 1, 2 * i + 2
        if left < n and values[left] < values[i] or right < n and values[right] < values[i]:
            return False
    return True

if __name__ == "__main__":
    assert is_min_heap_array([1, 3, 2, 7, 4])
    assert not is_min_heap_array([2, 1])
    assert is_min_heap_array([])
'''
    },

    # 2. NESTED LOOP AND COMPLEX CONDITIONAL (17 programs: P0568 - P0584)
    "P0568": {
        "domain": "Matrix & Grid Operations",
        "task": "Count land cells on the coastline of a binary map",
        "category": "Nested loop and complex conditional",
        "code": '''def coastline_cells(grid):
    rows, cols = len(grid), len(grid[0])
    coast = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 1:
                continue
            edge = r == 0 or c == 0 or r == rows - 1 or c == cols - 1
            if edge or grid[r - 1][c] == 0 or grid[r + 1][c] == 0 or grid[r][c - 1] == 0 or grid[r][c + 1] == 0:
                coast += 1
    return coast

if __name__ == "__main__":
    island = [[0, 0, 0, 0], [0, 1, 1, 0], [0, 1, 1, 0]]
    island.append([0, 0, 0, 0])
    assert coastline_cells(island) == 4
    assert coastline_cells([[1, 1, 1], [1, 1, 1], [1, 1, 1]]) == 8
'''
    },
    "P0569": {
        "domain": "Matrix & Grid Operations",
        "task": "Centres of plus-shaped patterns of one value in a grid",
        "category": "Nested loop and complex conditional",
        "code": '''def plus_shape_centers(grid, value):
    centers = []
    for r in range(1, len(grid) - 1):
        row = grid[r]
        for c in range(1, len(row) - 1):
            col_ok = grid[r - 1][c] == value and grid[r + 1][c] == value
            if row[c] == value and col_ok and row[c - 1] == value and row[c + 1] == value:
                centers.append((r, c))
    return centers

if __name__ == "__main__":
    g = [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    assert plus_shape_centers(g, 1) == [(1, 1)]
    assert plus_shape_centers(g, 0) == []
'''
    },
    "P0570": {
        "domain": "Matrix & Grid Operations",
        "task": "Detect k pieces in a row on any down-right diagonal of a board",
        "category": "Nested loop and complex conditional",
        "code": '''def has_diagonal_run(board, player, k):
    n = len(board)
    for r in range(n):
        for c in range(n):
            run = 0
            while r + run < n and c + run < n and board[r + run][c + run] == player:
                run += 1
            if run >= k:
                return True
    return False

if __name__ == "__main__":
    board = ["XO.", ".XO", "..X"]
    assert has_diagonal_run(board, "X", 3)
    assert has_diagonal_run(board, "O", 2)
    assert not has_diagonal_run(board, "O", 3)
'''
    },
    "P0571": {
        "domain": "Graph or Tree Traversal",
        "task": "Even-degree nodes at an exact BFS distance from a start node",
        "category": "Nested loop and complex conditional",
        "code": '''from collections import deque

def even_degree_at_distance(adj, start, distance):
    depth = {start: 0}
    queue = deque([start])
    hits = []
    while queue:
        node = queue.popleft()
        for nb in adj.get(node, ()):
            if nb not in depth:
                depth[nb] = depth[node] + 1
                queue.append(nb)
        if depth[node] == distance and len(adj.get(node, ())) % 2 == 0 and node != start:
            hits.append(node)
    return sorted(hits)

if __name__ == "__main__":
    adj = {"a": ["b", "c"], "b": ["a", "d"]}
    adj["c"] = ["a"]
    adj["d"] = ["b"]
    assert even_degree_at_distance(adj, "a", 1) == ["b"]
    assert even_degree_at_distance(adj, "a", 2) == []
'''
    },
    "P0572": {
        "domain": "Graph or Tree Traversal",
        "task": "Count triangles in an undirected graph given as neighbour sets",
        "category": "Nested loop and complex conditional",
        "code": '''def undirected_triangle_count(adj):
    total = 0
    for a in sorted(adj):
        for b in adj[a]:
            for c in adj[b]:
                if a < b < c and a in adj[c] and c != a:
                    total += 1
    return total

if __name__ == "__main__":
    adj = {"a": {"b", "c", "d"}, "b": {"a", "c"}}
    adj["c"] = {"a", "b"}
    adj["d"] = {"a"}
    assert undirected_triangle_count(adj) == 1
    assert undirected_triangle_count({"x": set()}) == 0
'''
    },
    "P0573": {
        "domain": "Searching and Sorting",
        "task": "Merge several sorted lists by repeatedly scanning their heads",
        "category": "Nested loop and complex conditional",
        "code": '''def merge_by_head_scan(lists):
    heads = [0] * len(lists)
    merged = []
    while True:
        best = -1
        for i, seq in enumerate(lists):
            if heads[i] < len(seq) and (best == -1 or seq[heads[i]] < lists[best][heads[best]]):
                best = i
        if best == -1:
            return merged
        merged.append(lists[best][heads[best]])
        heads[best] += 1

if __name__ == "__main__":
    assert merge_by_head_scan([[1, 4, 9], [2, 3], [], [5]]) == [1, 2, 3, 4, 5, 9]
    assert merge_by_head_scan([]) == []
'''
    },
    "P0574": {
        "domain": "Data Aggregation and Statistics",
        "task": "Pivot non-refunded sales into region by month totals",
        "category": "Nested loop and complex conditional",
        "code": '''def pivot_sales(rows, regions, months):
    table = {r: {m: 0 for m in months} for r in regions}
    for region in regions:
        for region_name, month, amount, refunded in rows:
            if region_name == region and month in table[region] and not refunded:
                table[region][month] += amount
    return table

if __name__ == "__main__":
    rows = [("N", "jan", 5, False), ("N", "jan", 3, True)]
    rows.append(("S", "feb", 4, False))
    table = pivot_sales(rows, ["N", "S"], ["jan", "feb"])
    assert table == {"N": {"jan": 5, "feb": 0}, "S": {"jan": 0, "feb": 4}}
'''
    },
    "P0575": {
        "domain": "String Processing & Text Analysis",
        "task": "Distinct palindromic words of a minimum length across sentences",
        "category": "Nested loop and complex conditional",
        "code": '''def palindromic_words(sentences, min_len):
    found = []
    for sentence in sentences:
        for raw in sentence.split():
            w = raw.strip(".,!?").lower()
            if len(w) >= min_len and w == w[::-1] and w.isalpha() and w not in found:
                found.append(w)
    return found

if __name__ == "__main__":
    text = ["Anna saw a racecar.", "Wow, level up!"]
    assert palindromic_words(text, 3) == ["anna", "racecar", "wow", "level"]
    assert palindromic_words(text, 6) == ["racecar"]
'''
    },
    "P0576": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Pairs of bookings that overlap in the same room",
        "category": "Nested loop and complex conditional",
        "code": '''def double_bookings(bookings):
    clashes = []
    for i in range(len(bookings)):
        for j in range(i + 1, len(bookings)):
            room_a, start_a, end_a = bookings[i]
            room_b, start_b, end_b = bookings[j]
            if room_a == room_b and start_a < end_b and start_b < end_a:
                clashes.append((i, j))
    return clashes

if __name__ == "__main__":
    bookings = [("A", 9, 11), ("A", 10, 12), ("B", 9, 10)]
    bookings.append(("A", 11, 13))
    assert double_bookings(bookings) == [(0, 1), (1, 3)]
'''
    },
    "P0577": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Customers served by bank tellers before their patience runs out",
        "category": "Nested loop and complex conditional",
        "code": '''def served_customers(arrivals, service, tellers, patience):
    free_at = [0] * tellers
    served = 0
    for t in arrivals:
        for k in range(tellers):
            wait = max(0, free_at[k] - t)
            if wait <= patience and free_at[k] == min(free_at) and service > 0:
                free_at[k] = max(free_at[k], t) + service
                served += 1
                break
    return served

if __name__ == "__main__":
    assert served_customers([0, 0, 0, 1], 5, 2, 2) == 2
    assert served_customers([0, 0, 0, 1], 5, 2, 10) == 4
'''
    },
    "P0578": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Name pairs whose non-negative scores add up to a total",
        "category": "Nested loop and complex conditional",
        "code": '''def complementary_pairs(scores, total):
    names = sorted(scores)
    pairs = []
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if scores[a] + scores[b] == total and scores[a] >= 0 and scores[b] >= 0:
                pairs.append((a, b))
    return pairs

if __name__ == "__main__":
    scores = {"x": 3, "y": 7, "z": 5, "w": -2, "v": 12}
    assert complementary_pairs(scores, 10) == [("x", "y")]
'''
    },
    "P0579": {
        "domain": "Numerical Computation",
        "task": "Non-negative integer solutions of ax + by = c inside a box",
        "category": "Nested loop and complex conditional",
        "code": '''def bounded_linear_solutions(a, b, c, bound):
    solutions = []
    for x in range(-bound, bound + 1):
        for y in range(-bound, bound + 1):
            if a * x + b * y == c and x >= 0 and y >= 0:
                solutions.append((x, y))
    return solutions

if __name__ == "__main__":
    assert bounded_linear_solutions(2, 3, 12, 6) == [(0, 4), (3, 2), (6, 0)]
    assert bounded_linear_solutions(2, 4, 7, 5) == []
'''
    },
    "P0580": {
        "domain": "Inventory and Record Management",
        "task": "SKUs whose stock counts disagree between warehouses",
        "category": "Nested loop and complex conditional",
        "code": '''def conflicting_stock(warehouses):
    seen = {}
    conflicts = set()
    for name, items in warehouses.items():
        for sku, qty in items.items():
            if sku in seen and seen[sku][1] != qty and seen[sku][0] != name:
                conflicts.add(sku)
            seen.setdefault(sku, (name, qty))
    return sorted(conflicts)

if __name__ == "__main__":
    w = {"north": {"a1": 5, "b2": 3}}
    w["south"] = {"a1": 5, "b2": 4, "c3": 1}
    assert conflicting_stock(w) == ["b2"]
'''
    },
    "P0581": {
        "domain": "Data Aggregation and Statistics",
        "task": "Tag pairs that co-occur in posts at least a minimum number of times",
        "category": "Nested loop and complex conditional",
        "code": '''def tag_cooccurrence(posts, minimum):
    pairs = {}
    for tags in posts:
        unique = sorted(set(tags))
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                key = (unique[i], unique[j])
                pairs[key] = pairs.get(key, 0) + 1
    strong = {}
    for key, count in pairs.items():
        if count >= minimum and key[0] != key[1] and "misc" not in key:
            strong[key] = count
    return strong

if __name__ == "__main__":
    posts = [["py", "ml"], ["ml", "py", "misc"], ["py", "web"]]
    assert tag_cooccurrence(posts, 2) == {("ml", "py"): 2}
'''
    },
    "P0582": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Earliest quarter-hour slot free in every attendee calendar",
        "category": "Nested loop and complex conditional",
        "code": '''def common_free_slot(calendars, day_start, day_end, length):
    t = day_start
    while t + length <= day_end:
        clash = False
        for busy in calendars:
            for start, end in busy:
                if start < t + length and t < end and end > start:
                    clash = True
        if not clash:
            return t
        t += 15
    return -1

if __name__ == "__main__":
    cals = [[(540, 600)], [(570, 630), (700, 720)]]
    assert common_free_slot(cals, 480, 1020, 60) == 480
    assert common_free_slot(cals, 540, 1020, 60) == 630
    assert common_free_slot(cals, 540, 600, 60) == -1
'''
    },
    "P0583": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Lights-out puzzle state after toggling pressed cells and neighbours",
        "category": "Nested loop and complex conditional",
        "code": '''def press_lights(grid, presses):
    rows, cols = len(grid), len(grid[0])
    state = [row[:] for row in grid]
    for r, c in presses:
        for dr, dc in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols:
                state[nr][nc] = 1 - state[nr][nc]
    return state

if __name__ == "__main__":
    dark = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    assert press_lights(dark, [(1, 1)]) == [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    assert press_lights(dark, [(0, 0)]) == [[1, 1, 0], [1, 0, 0], [0, 0, 0]]
'''
    },
    "P0584": {
        "domain": "Inventory and Record Management",
        "task": "Match returned items to receipts within the return window",
        "category": "Nested loop and complex conditional",
        "code": '''def match_returns(receipts, returns, max_days):
    stock = {rid: list(items) for rid, items, _ in receipts}
    matched = {}
    for ret_id, sku, day in returns:
        for receipt_id, _, bought_day in receipts:
            if sku in stock[receipt_id] and 0 <= day - bought_day <= max_days and ret_id not in matched:
                matched[ret_id] = receipt_id
                stock[receipt_id].remove(sku)
    return matched

if __name__ == "__main__":
    receipts = [("r1", ["a", "b"], 1), ("r2", ["a"], 5)]
    rets = [("x1", "a", 3), ("x2", "a", 6), ("x3", "b", 40)]
    assert match_returns(receipts, rets, 30) == {"x1": "r1", "x2": "r2"}
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0585 - P0590)
    "P0585": {
        "domain": "String Processing & Text Analysis",
        "task": "Longest shared leading text of several words by column scan",
        "category": "Nested loop only",
        "code": '''def shared_leading_text(words):
    if not words:
        return ""
    prefix = []
    for i in range(min(len(w) for w in words)):
        letter = words[0][i]
        for w in words[1:]:
            if w[i] != letter:
                return "".join(prefix)
        prefix.append(letter)
    return "".join(prefix)

if __name__ == "__main__":
    assert shared_leading_text(["flower", "flow", "flight"]) == "fl"
    assert shared_leading_text(["a"]) == "a"
    assert shared_leading_text([]) == ""
'''
    },
    "P0586": {
        "domain": "Numerical Computation",
        "task": "Primes in a closed range by trial division",
        "category": "Nested loop only",
        "code": '''def trial_division_primes(low, high):
    found = []
    for n in range(max(2, low), high + 1):
        d = 2
        while d * d <= n and n % d:
            d += 1
        if d * d > n:
            found.append(n)
    return found

if __name__ == "__main__":
    assert trial_division_primes(10, 30) == [11, 13, 17, 19, 23, 29]
    assert trial_division_primes(0, 3) == [2, 3]
'''
    },
    "P0587": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Element frequencies across nested lists ranked by count",
        "category": "Nested loop only",
        "code": '''def flatten_and_count(nested):
    counts = {}
    for group in nested:
        for item in group:
            counts[item] = counts.get(item, 0) + 1
    return sorted(counts.items(), key=lambda p: (-p[1], p[0]))

if __name__ == "__main__":
    groups = [["a", "b"], ["b"], ["c", "b", "a"]]
    assert flatten_and_count(groups) == [("b", 3), ("a", 2), ("c", 1)]
'''
    },
    "P0588": {
        "domain": "Searching and Sorting",
        "task": "Largest k values by repeated maximum scans without sorting",
        "category": "Nested loop only",
        "code": '''def top_k_by_scanning(values, k):
    pool = list(values)
    chosen = []
    while pool and len(chosen) < k:
        best = 0
        for i in range(1, len(pool)):
            if pool[i] > pool[best]:
                best = i
        chosen.append(pool.pop(best))
    return chosen

if __name__ == "__main__":
    assert top_k_by_scanning([4, 9, 1, 7], 2) == [9, 7]
    assert top_k_by_scanning([1], 3) == [1]
'''
    },
    "P0589": {
        "domain": "Graph or Tree Traversal",
        "task": "Adjacency matrix and node degrees from an undirected edge list",
        "category": "Nested loop only",
        "code": '''def adjacency_with_degrees(n, edges):
    matrix = [[0] * n for _ in range(n)]
    for u, v in edges:
        matrix[u][v] = 1
        matrix[v][u] = 1
    degrees = []
    for row in matrix:
        total = 0
        for cell in row:
            total += cell
        degrees.append(total)
    return matrix, degrees

if __name__ == "__main__":
    edges = [(0, 1), (1, 2)]
    matrix, degrees = adjacency_with_degrees(3, edges)
    assert degrees == [1, 2, 1]
    assert matrix[0] == [0, 1, 0]
'''
    },
    "P0590": {
        "domain": "Matrix & Grid Operations",
        "task": "Kronecker product of two small matrices",
        "category": "Nested loop only",
        "code": '''def kron_expand(a, b):
    rows_b, cols_b = len(b), len(b[0])
    width = len(a[0]) * cols_b
    height = len(a) * rows_b
    out = [[0] * width for _ in range(height)]
    for i, row in enumerate(a):
        for j, x in enumerate(row):
            for p in range(rows_b):
                for q in range(cols_b):
                    out[i * rows_b + p][j * cols_b + q] = x * b[p][q]
    return out

if __name__ == "__main__":
    swap = [[0, 1], [1, 0]]
    assert kron_expand([[1, 2]], swap) == [[0, 1, 0, 2], [1, 0, 2, 0]]
'''
    },

    # 4. LONG STATEMENT AND NESTED LOOP (6 programs: P0591 - P0596)
    "P0591": {
        "domain": "Matrix & Grid Operations",
        "task": "Sobel edge magnitude for the interior pixels of an image",
        "category": "Long statement and nested loop",
        "code": '''def sobel_magnitude(img):
    h, w = len(img), len(img[0])
    out = [[0] * w for _ in range(h)]
    for r in range(1, h - 1):
        for c in range(1, w - 1):
            gx = img[r - 1][c + 1] + 2 * img[r][c + 1] + img[r + 1][c + 1] - img[r - 1][c - 1] - 2 * img[r][c - 1] - img[r + 1][c - 1]
            gy = img[r + 1][c - 1] + 2 * img[r + 1][c] + img[r + 1][c + 1] - img[r - 1][c - 1] - 2 * img[r - 1][c] - img[r - 1][c + 1]
            out[r][c] = abs(gx) + abs(gy)
    return out

if __name__ == "__main__":
    edge = [[0, 0, 9], [0, 0, 9], [0, 0, 9]]
    assert sobel_magnitude(edge)[1][1] == 36
    assert sobel_magnitude(edge)[0][0] == 0
'''
    },
    "P0592": {
        "domain": "Graph or Tree Traversal",
        "task": "Total cost of several routes with tolls and fees on each leg",
        "category": "Long statement and nested loop",
        "code": '''def route_costs(graph, routes):
    totals = []
    for route in routes:
        cost = 0
        for a, b in zip(route, route[1:]):
            cost = cost + graph[a][b]["distance"] * graph[a][b].get("toll_factor", 1.0) + graph[a][b].get("fee", 0)
        totals.append(round(cost, 2))
    return totals

if __name__ == "__main__":
    g = {"a": {}, "b": {}}
    g["a"]["b"] = {"distance": 10}
    g["b"]["c"] = {"distance": 5, "fee": 2}
    assert route_costs(g, [["a", "b", "c"], ["a", "b"]]) == [17.0, 10.0]
'''
    },
    "P0593": {
        "domain": "String Processing & Text Analysis",
        "task": "Guess a Caesar cipher shift by counting common English letters",
        "category": "Long statement and nested loop",
        "code": '''def guess_caesar_shift(cipher):
    common = "etaoinshr"
    best_shift, best_score = 0, -1
    for shift in range(26):
        score = 0
        for ch in cipher.lower():
            if ch.isalpha():
                decoded = chr((ord(ch) - ord("a") - shift + 26) % 26 + ord("a"))
                score += 1 if decoded in common else 0
        if score > best_score:
            best_shift, best_score = shift, score
    return best_shift

if __name__ == "__main__":
    assert guess_caesar_shift("wkh vhfuhw lv qrw khuh") == 3
    assert guess_caesar_shift("the rain in spain") == 0
'''
    },
    "P0594": {
        "domain": "Numerical Computation",
        "task": "Midpoint-rule double integral of a quadratic form over a rectangle",
        "category": "Long statement and nested loop",
        "code": '''def double_integral_midpoint(coeffs, x_range, y_range, steps):
    a, b, c = coeffs
    (x0, x1), (y0, y1) = x_range, y_range
    hx, hy = (x1 - x0) / steps, (y1 - y0) / steps
    total = 0.0
    for i in range(steps):
        for j in range(steps):
            x, y = x0 + (i + 0.5) * hx, y0 + (j + 0.5) * hy
            cell_value = a * x * x * hx * hy + b * x * y * hx * hy + c * y * y * hx * hy
            total += cell_value
    return total

if __name__ == "__main__":
    unit = (0.0, 1.0)
    assert abs(double_integral_midpoint((1, 0, 0), unit, unit, 50) - 1 / 3) < 1e-3
    assert abs(double_integral_midpoint((0, 1, 0), unit, unit, 10) - 0.25) < 1e-9
'''
    },
    "P0595": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Join two lists of record dictionaries on a shared key",
        "category": "Long statement and nested loop",
        "code": '''def join_records_on(left, right, key):
    joined = []
    for l_row in left:
        for r_row in right:
            if l_row[key] == r_row[key]:
                joined.append({**l_row, **{k: v for k, v in r_row.items() if k != key}})
    return joined

if __name__ == "__main__":
    left = [{"id": 1, "n": "a"}, {"id": 2, "n": "b"}]
    right = [{"id": 2, "q": 5}]
    assert join_records_on(left, right, "id") == [{"id": 2, "n": "b", "q": 5}]
'''
    },
    "P0596": {
        "domain": "Searching and Sorting",
        "task": "Stable counting sort of keyed records with a position checksum",
        "category": "Long statement and nested loop",
        "code": '''def counting_sort_records(records, max_key):
    buckets = [[] for _ in range(max_key + 1)]
    for rec in records:
        buckets[rec[0]].append(rec)
    ordered = []
    for bucket in buckets:
        for rec in bucket:
            ordered.append(rec)
    checksum = sum(rec[0] * (i + 1) for i, rec in enumerate(ordered)) + len(ordered) * max_key
    return ordered, checksum

if __name__ == "__main__":
    recs = [(2, "b"), (0, "a"), (2, "c"), (1, "d")]
    ordered, checksum = counting_sort_records(recs, 2)
    assert ordered == [(0, "a"), (1, "d"), (2, "b"), (2, "c")]
    assert checksum == 24
'''
    },

    # 5. NONE (2 programs: P0597 - P0598)
    "P0597": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Score one roll of five dice under triple and single-face rules",
        "category": "None",
        "code": '''from collections import Counter

def score_dice_roll(dice):
    counts = Counter(dice)
    score = 0
    for face, n in counts.items():
        if n >= 3:
            score += face * 100 if face != 1 else 1000
            n -= 3
        if face == 1:
            score += n * 100
        elif face == 5:
            score += n * 50
    return score

if __name__ == "__main__":
    assert score_dice_roll([1, 1, 1, 5, 2]) == 1050
    assert score_dice_roll([3, 3, 3, 3, 5]) == 350
    assert score_dice_roll([2, 3, 4, 6, 6]) == 0
'''
    },
    "P0598": {
        "domain": "Inventory and Record Management",
        "task": "Fixed-width shelf label line with truncated name and bin code",
        "category": "None",
        "code": '''def label_line(sku, name, qty, bin_code, width=32):
    short = name if len(name) <= 16 else name[:15] + "~"
    qty_text = str(qty).rjust(4)
    line = f"{sku:<8}{short:<16}{qty_text}"
    if bin_code:
        line = line[:width - 4] + bin_code[:4]
    return line[:width]

if __name__ == "__main__":
    label = label_line("A1", "Widget", 7, "B3")
    assert label.startswith("A1      Widget") and label.endswith("   7B3")
    assert label_line("Z9", "Extra long product name", 120, "")[8:24] == "Extra long prod~"
'''
    },

    # 6. LONG STATEMENT ONLY (2 programs: P0599 - P0600)
    "P0599": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Finish times of queued print jobs with warm-up and duplex slowdown",
        "category": "Long statement only",
        "code": '''def print_queue_finish_times(jobs, pages_per_minute, warmup):
    clock = 0.0
    finishes = []
    for pages, copies, duplex in jobs:
        clock = clock + warmup + pages * copies / pages_per_minute * (1.6 if duplex else 1.0)
        finishes.append(round(clock, 1))
    return finishes

if __name__ == "__main__":
    jobs = [(10, 2, False), (5, 1, True)]
    assert print_queue_finish_times(jobs, 20, 0.5) == [1.5, 2.4]
'''
    },
    "P0600": {
        "domain": "Data Aggregation and Statistics",
        "task": "Bias-corrected exponential moving mean and variance of a series",
        "category": "Long statement only",
        "code": '''def ewma_mean_variance(series, beta):
    avg = 0.0
    variance = 0.0
    out = []
    for t, x in enumerate(series, start=1):
        avg = beta * avg + (1 - beta) * x
        corrected = avg / (1 - beta ** t)
        variance = beta * variance + (1 - beta) * (x - corrected) * (x - corrected)
        out.append((round(corrected, 4), round(variance, 4)))
    return out

if __name__ == "__main__":
    assert ewma_mean_variance([10, 10, 10], 0.5) == [(10.0, 0.0)] * 3
    mean, var = ewma_mean_variance([0, 10], 0.5)[1]
    assert abs(mean - 6.6667) < 1e-4 and abs(var - 5.5556) < 1e-4
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 12",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v12.0-expansion",
        "programs": BATCH12_PROGRAMS,
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