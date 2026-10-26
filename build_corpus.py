"""
build_corpus.py
Writes the Batch 11 (P0501-P0550) programs into program_corpus/programs and
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

BATCH11_PROGRAMS = {
    # 1. COMPLEX CONDITIONAL ONLY (12 programs: P0501 - P0512)
    "P0501": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Next traffic signal phase from waiting cars and elapsed time",
        "category": "Complex conditional only",
        "code": '''def advance_signal_phase(phase: str, waiting: int, elapsed: int, emergency: bool) -> str:
    if emergency:
        return "all_red"
    if phase == "green" and elapsed >= 30 and waiting > 0:
        return "yellow"
    if phase == "yellow" and elapsed >= 4:
        return "red"
    if phase == "red" and (elapsed >= 25 or waiting > 5):
        return "green"
    return phase

if __name__ == "__main__":
    assert advance_signal_phase("green", 3, 31, False) == "yellow"
    assert advance_signal_phase("green", 0, 31, False) == "green"
    assert advance_signal_phase("red", 6, 10, False) == "green"
    assert advance_signal_phase("yellow", 0, 1, True) == "all_red"
'''
    },
    "P0502": {
        "domain": "Inventory and Record Management",
        "task": "Library loan eligibility from member tier, overdue days and item kind",
        "category": "Complex conditional only",
        "code": '''def can_borrow_item(member: dict, item: dict, loans: int) -> bool:
    limit = 8 if member["tier"] == "premium" else 4
    overdue = member.get("overdue_days", 0)
    if item.get("reference_only"):
        return False
    if member["active"] and overdue == 0 and loans < limit:
        return True
    elif member["active"] and overdue <= 3 and loans < 2 and item["kind"] != "dvd":
        return True
    return False

if __name__ == "__main__":
    m = {"tier": "basic", "active": True}
    assert can_borrow_item(m, {"kind": "book"}, 3)
    assert not can_borrow_item(m, {"kind": "book"}, 4)
    late = {"tier": "basic", "active": True, "overdue_days": 2}
    assert can_borrow_item(late, {"kind": "book"}, 1)
    assert not can_borrow_item(late, {"kind": "dvd"}, 1)
'''
    },
    "P0503": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Approve a meeting room booking against opening hours and capacity",
        "category": "Complex conditional only",
        "code": '''def approve_room_booking(start: int, end: int, attendees: int, room: dict) -> str:
    duration = end - start
    if duration <= 0:
        return "invalid"
    open_ok = start >= room["opens"] and end <= room["closes"]
    if open_ok and attendees <= room["capacity"] and duration <= 240:
        return "approved"
    if attendees > room["capacity"]:
        return "too_small"
    return "needs_review"

if __name__ == "__main__":
    room = {"opens": 480, "closes": 1080, "capacity": 10}
    assert approve_room_booking(540, 660, 6, room) == "approved"
    assert approve_room_booking(540, 660, 12, room) == "too_small"
    assert approve_room_booking(420, 540, 4, room) == "needs_review"
    assert approve_room_booking(600, 600, 2, room) == "invalid"
'''
    },
    "P0504": {
        "domain": "String Processing & Text Analysis",
        "task": "Classify log line severity with keyword rules",
        "category": "Complex conditional only",
        "code": '''def classify_log_severity(line: str) -> str:
    text = line.lower()
    has_code = any(ch.isdigit() for ch in text)
    if "fatal" in text or "panic" in text or ("error" in text and has_code):
        return "critical"
    if "warn" in text and not text.startswith("debug"):
        return "warning"
    return "info"

if __name__ == "__main__":
    assert classify_log_severity("FATAL disk failure") == "critical"
    assert classify_log_severity("error 503 upstream") == "critical"
    assert classify_log_severity("error upstream") == "info"
    assert classify_log_severity("WARN low memory") == "warning"
    assert classify_log_severity("debug: warn flag") == "info"
'''
    },
    "P0505": {
        "domain": "Numerical Computation",
        "task": "Cube root by Newton iteration with tolerance and iteration cap",
        "category": "Complex conditional only",
        "code": '''def newton_cube_root(value: float, tolerance: float = 1e-9) -> float:
    if value == 0:
        return 0.0
    guess = value if abs(value) > 1 else 1.0
    step = 1.0
    iterations = 0
    while abs(step) > tolerance and iterations < 100 and guess != 0:
        step = (guess ** 3 - value) / (3 * guess ** 2)
        guess -= step
        iterations += 1
    return guess

if __name__ == "__main__":
    assert abs(newton_cube_root(27.0) - 3.0) < 1e-6
    assert abs(newton_cube_root(-8.0) + 2.0) < 1e-6
    assert newton_cube_root(0) == 0.0
'''
    },
    "P0506": {
        "domain": "Data Aggregation and Statistics",
        "task": "Indexes of sensor readings out of range or jumping too far",
        "category": "Complex conditional only",
        "code": '''def flag_suspicious_readings(readings: list[float], low: float, high: float) -> list[int]:
    flagged = []
    previous = None
    for index, value in enumerate(readings):
        jump = 0.0 if previous is None else abs(value - previous)
        if value < low or value > high or jump > (high - low) / 2:
            flagged.append(index)
        previous = value
    return flagged

if __name__ == "__main__":
    data = [5.0, 6.0, 30.0, 7.0, -1.0]
    assert flag_suspicious_readings(data, 0.0, 20.0) == [2, 3, 4]
    assert flag_suspicious_readings([], 0.0, 1.0) == []
'''
    },
    "P0507": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Merge user setting overrides that are known, same-typed and unlocked",
        "category": "Complex conditional only",
        "code": '''def merge_user_settings(defaults: dict, overrides: dict, locked: set) -> dict:
    merged = dict(defaults)
    for key, value in overrides.items():
        known = key in defaults
        same_type = known and type(value) is type(defaults[key])
        if known and same_type and key not in locked:
            merged[key] = value
    return merged

if __name__ == "__main__":
    base = {"theme": "light", "font": 12, "beta": False}
    new = {"theme": "dark", "font": "big", "beta": True}
    expected = {"theme": "dark", "font": 12, "beta": False}
    assert merge_user_settings(base, new, {"beta"}) == expected
'''
    },
    "P0508": {
        "domain": "Searching and Sorting",
        "task": "Peak index of a unimodal list by ternary search",
        "category": "Complex conditional only",
        "code": '''def unimodal_peak_index(values: list[int]) -> int:
    if not values:
        return -1
    lo, hi = 0, len(values) - 1
    steps = 0
    while lo < hi and hi - lo > 2 and steps < 64:
        steps += 1
        third = (hi - lo) // 3
        left, right = lo + third, hi - third
        if values[left] < values[right]:
            lo = left + 1
        else:
            hi = right
    best = lo
    for index in range(lo, hi + 1):
        if values[index] > values[best]:
            best = index
    return best

if __name__ == "__main__":
    assert unimodal_peak_index([1, 3, 8, 12, 9, 4, 2]) == 3
    assert unimodal_peak_index([5, 4, 3]) == 0
    assert unimodal_peak_index([1, 2]) == 1
    assert unimodal_peak_index([]) == -1
'''
    },
    "P0509": {
        "domain": "Inventory and Record Management",
        "task": "Decide whether projected stock after lead time needs a reorder",
        "category": "Complex conditional only",
        "code": '''def should_place_reorder(sku: dict, daily_demand: float, lead_days: int) -> bool:
    on_hand = sku["on_hand"] + sku.get("incoming", 0)
    safety = sku.get("safety_stock", 0)
    projected = on_hand - daily_demand * lead_days
    if sku.get("discontinued"):
        return False
    if projected < safety and daily_demand > 0 and not sku.get("frozen", False):
        return True
    return False

if __name__ == "__main__":
    item = {"on_hand": 20, "incoming": 5, "safety_stock": 10}
    assert should_place_reorder(item, 4.0, 5)
    assert not should_place_reorder(item, 2.0, 5)
    assert not should_place_reorder({"on_hand": 0, "frozen": True}, 1.0, 3)
'''
    },
    "P0510": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Elevator direction choice from pending floor requests",
        "category": "Complex conditional only",
        "code": '''def choose_elevator_direction(floor: int, requests: list[int], moving_up: bool) -> str:
    above = [r for r in requests if r > floor]
    below = [r for r in requests if r < floor]
    if not requests:
        return "idle"
    if moving_up and above or not below and above:
        return "up"
    if below:
        return "down"
    return "open"

if __name__ == "__main__":
    assert choose_elevator_direction(3, [5, 1], True) == "up"
    assert choose_elevator_direction(3, [5, 1], False) == "down"
    assert choose_elevator_direction(3, [1], True) == "down"
    assert choose_elevator_direction(3, [3], True) == "open"
    assert choose_elevator_direction(3, [], True) == "idle"
'''
    },
    "P0511": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Approve a shift swap by role, weekly hour cap and rest time",
        "category": "Complex conditional only",
        "code": '''def approve_shift_swap(giver: dict, taker: dict, shift_hours: int) -> bool:
    if giver["role"] != taker["role"]:
        return False
    new_total = taker["weekly_hours"] + shift_hours
    rested = taker.get("rest_hours", 24) >= 11
    if new_total <= 48 and rested and not taker.get("on_leave", False):
        return True
    return False

if __name__ == "__main__":
    a = {"role": "nurse", "weekly_hours": 36}
    b = {"role": "nurse", "weekly_hours": 40, "rest_hours": 12}
    assert approve_shift_swap(a, b, 8)
    assert not approve_shift_swap(a, b, 12)
    assert not approve_shift_swap(a, {"role": "porter", "weekly_hours": 0}, 8)
'''
    },
    "P0512": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate a user handle by first character, allowed symbols and length",
        "category": "Complex conditional only",
        "code": '''def is_valid_handle(handle: str) -> bool:
    if not handle:
        return False
    first = handle[0]
    allowed = all(ch.isalnum() or ch in "_." for ch in handle)
    if first.isalpha() and allowed and 3 <= len(handle) <= 15:
        return not handle.endswith(".")
    return False

if __name__ == "__main__":
    assert is_valid_handle("alice_99")
    assert is_valid_handle("x.y.z")
    assert not is_valid_handle("9lives")
    assert not is_valid_handle("ab")
    assert not is_valid_handle("bob.")
'''
    },

    # 2. NESTED LOOP AND COMPLEX CONDITIONAL (12 programs: P0513 - P0524)
    "P0513": {
        "domain": "Matrix & Grid Operations",
        "task": "Count grid cells above a minimum that beat both vertical neighbours",
        "category": "Nested loop and complex conditional",
        "code": '''def count_vertical_peaks(grid: list[list[int]], minimum: int) -> int:
    rows, cols = len(grid), len(grid[0])
    peaks = 0
    for r in range(rows):
        for c in range(cols):
            value = grid[r][c]
            up = grid[r - 1][c] if r > 0 else -1
            down = grid[r + 1][c] if r < rows - 1 else -1
            if value >= minimum and value > up and value > down:
                peaks += 1
    return peaks

if __name__ == "__main__":
    grid = [[1, 5, 1], [4, 2, 6], [1, 1, 1]]
    assert count_vertical_peaks(grid, 3) == 3
    assert count_vertical_peaks(grid, 9) == 0
'''
    },
    "P0514": {
        "domain": "Matrix & Grid Operations",
        "task": "Top-left corners of uniform non-zero 2x2 blocks in a grid",
        "category": "Nested loop and complex conditional",
        "code": '''def uniform_square_corners(grid: list[list[int]]) -> list[tuple[int, int]]:
    corners = []
    for r in range(len(grid) - 1):
        for c in range(len(grid[0]) - 1):
            v = grid[r][c]
            right, below = grid[r][c + 1], grid[r + 1][c]
            if v != 0 and v == right and v == below and v == grid[r + 1][c + 1]:
                corners.append((r, c))
    return corners

if __name__ == "__main__":
    assert uniform_square_corners([[1, 1, 0], [1, 1, 0], [2, 2, 2]]) == [(0, 0)]
    assert uniform_square_corners([[0, 0], [0, 0]]) == []
'''
    },
    "P0515": {
        "domain": "Graph or Tree Traversal",
        "task": "Nodes reachable within a hop limit while avoiding blocked nodes",
        "category": "Nested loop and complex conditional",
        "code": '''from collections import deque

def reachable_within_hops(graph: dict[str, list[str]], start: str, blocked: set[str], max_hops: int) -> set[str]:
    seen = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            hops = seen[node] + 1
            if nxt not in seen and nxt not in blocked and hops <= max_hops:
                seen[nxt] = hops
                queue.append(nxt)
    return set(seen)

if __name__ == "__main__":
    g = {"a": ["b", "c"], "b": ["d"], "c": ["d"], "d": ["e"]}
    assert reachable_within_hops(g, "a", {"c"}, 2) == {"a", "b", "d"}
    assert reachable_within_hops(g, "a", set(), 1) == {"a", "b", "c"}
'''
    },
    "P0516": {
        "domain": "Graph or Tree Traversal",
        "task": "Leaves whose weighted root path total falls inside a range",
        "category": "Nested loop and complex conditional",
        "code": '''def qualifying_leaf_paths(tree: dict[str, list[str]], weight: dict[str, int], root: str, low: int, high: int) -> list[str]:
    found = []
    stack = [(root, weight[root])]
    while stack:
        node, total = stack.pop()
        children = tree.get(node, [])
        if not children and low <= total <= high and node != root:
            found.append(node)
        for child in children:
            stack.append((child, total + weight[child]))
    return sorted(found)

if __name__ == "__main__":
    t = {"r": ["a", "b"], "a": ["c"]}
    w = {"r": 1, "a": 2, "b": 9, "c": 3}
    assert qualifying_leaf_paths(t, w, "r", 5, 8) == ["c"]
    assert qualifying_leaf_paths(t, w, "r", 5, 10) == ["b", "c"]
'''
    },
    "P0517": {
        "domain": "Searching and Sorting",
        "task": "Count two-pointer pair matches for several target sums",
        "category": "Nested loop and complex conditional",
        "code": '''def count_pair_sums(values: list[int], targets: list[int]) -> dict[int, int]:
    ordered = sorted(values)
    counts = {}
    for target in targets:
        i, j = 0, len(ordered) - 1
        found = 0
        while i < j and ordered[i] <= target and found < 10:
            pair = ordered[i] + ordered[j]
            if pair == target:
                found += 1
                i += 1
                j -= 1
            elif pair < target:
                i += 1
            else:
                j -= 1
        counts[target] = found
    return counts

if __name__ == "__main__":
    nums = [1, 2, 3, 4, 5, 6]
    assert count_pair_sums(nums, [7, 3, 20]) == {7: 3, 3: 1, 20: 0}
'''
    },
    "P0518": {
        "domain": "Data Aggregation and Statistics",
        "task": "Total valid survey scores per question for adult respondents",
        "category": "Nested loop and complex conditional",
        "code": '''def tally_survey_scores(responses: list[dict], questions: list[str], min_age: int) -> dict[str, int]:
    totals = {q: 0 for q in questions}
    for person in responses:
        for q in questions:
            score = person["answers"].get(q)
            if score is not None and person["age"] >= min_age and 1 <= score <= 5:
                totals[q] += score
    return totals

if __name__ == "__main__":
    a = {"age": 30, "answers": {"q1": 4, "q2": 9}}
    b = {"age": 17, "answers": {"q1": 5}}
    assert tally_survey_scores([a, b], ["q1", "q2"], 18) == {"q1": 4, "q2": 0}
'''
    },
    "P0519": {
        "domain": "String Processing & Text Analysis",
        "task": "Letter pairs of distinct letters that recur across words",
        "category": "Nested loop and complex conditional",
        "code": '''def frequent_letter_pairs(words: list[str], least: int) -> list[str]:
    counts = {}
    for word in words:
        for i in range(len(word) - 1):
            a, b = word[i], word[i + 1]
            if a.isalpha() and b.isalpha() and a != b:
                pair = (a + b).lower()
                counts[pair] = counts.get(pair, 0) + 1
    return sorted(p for p, n in counts.items() if n >= least)

if __name__ == "__main__":
    words = ["hello", "yellow", "mellow"]
    assert frequent_letter_pairs(words, 3) == ["el", "lo"]
    assert frequent_letter_pairs(["a1b"], 1) == []
'''
    },
    "P0520": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Greedy task assignment to skilled workers within hour capacity",
        "category": "Nested loop and complex conditional",
        "code": '''def assign_tasks_greedily(tasks: list[tuple[str, int, str]], workers: list[tuple[str, int, set[str]]]) -> dict[str, str]:
    plan = {}
    load = {name: 0 for name, _, _ in workers}
    for task_id, hours, skill in tasks:
        for name, capacity, skills in workers:
            fits = load[name] + hours <= capacity
            if fits and skill in skills and task_id not in plan:
                plan[task_id] = name
                load[name] += hours
    return plan

if __name__ == "__main__":
    crew = [("ana", 6, {"weld"}), ("raj", 8, {"weld", "paint"})]
    jobs = [("t1", 4, "weld"), ("t2", 4, "weld")]
    jobs.append(("t3", 3, "paint"))
    assert assign_tasks_greedily(jobs, crew) == {"t1": "ana", "t2": "raj", "t3": "raj"}
'''
    },
    "P0521": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "One step of fire spreading through a forest grid with wind",
        "category": "Nested loop and complex conditional",
        "code": '''def spread_fire_once(forest: list[str], wind_east: bool) -> list[str]:
    rows, cols = len(forest), len(forest[0])
    nxt = [list(row) for row in forest]
    for r in range(rows):
        for c in range(cols):
            if forest[r][c] != "T":
                continue
            west = c > 0 and forest[r][c - 1] == "F"
            north = r > 0 and forest[r - 1][c] == "F"
            if west or north or (not wind_east and c < cols - 1 and forest[r][c + 1] == "F"):
                nxt[r][c] = "F"
    return ["".join(row) for row in nxt]

if __name__ == "__main__":
    assert spread_fire_once(["TFT", "TTT"], True) == ["TFF", "TFT"]
    assert spread_fire_once(["TFT", "TTT"], False) == ["FFF", "TFT"]
'''
    },
    "P0522": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Cleaned tags shared by more than one group, excluding banned tags",
        "category": "Nested loop and complex conditional",
        "code": '''def shared_tags(groups: list[list[str]], banned: set[str]) -> list[str]:
    seen_in = {}
    for index, group in enumerate(groups):
        for tag in set(group):
            clean = tag.strip().lower()
            if clean and clean not in banned and not clean.startswith("#"):
                seen_in.setdefault(clean, set()).add(index)
    common = [t for t, ids in seen_in.items() if len(ids) > 1]
    return sorted(common)

if __name__ == "__main__":
    groups = [["Red", "blue"], ["red ", "#x"]]
    groups.append(["BLUE", "green"])
    assert shared_tags(groups, {"green"}) == ["blue", "red"]
    assert shared_tags(groups, {"red", "blue"}) == []
'''
    },
    "P0523": {
        "domain": "Numerical Computation",
        "task": "Count even-sum lattice points inside a circular ring",
        "category": "Nested loop and complex conditional",
        "code": '''def lattice_points_in_ring(inner: int, outer: int) -> int:
    count = 0
    for x in range(-outer, outer + 1):
        for y in range(-outer, outer + 1):
            dist = x * x + y * y
            if inner * inner <= dist <= outer * outer and (x + y) % 2 == 0:
                count += 1
    return count

if __name__ == "__main__":
    assert lattice_points_in_ring(1, 2) == 8
    assert lattice_points_in_ring(1, 1) == 0
'''
    },
    "P0524": {
        "domain": "Inventory and Record Management",
        "task": "Order lines without a matching shipment of sufficient quantity",
        "category": "Nested loop and complex conditional",
        "code": '''def unmatched_order_lines(orders: list[tuple[str, str, int]], shipped: list[tuple[str, str, int]]) -> list[str]:
    missing = []
    for order_id, sku, qty in orders:
        matched = False
        for ship_order, ship_sku, ship_qty in shipped:
            if ship_order == order_id and ship_sku == sku and ship_qty >= qty:
                matched = True
                break
        if not matched:
            missing.append(f"{order_id}:{sku}")
    return missing

if __name__ == "__main__":
    orders = [("o1", "pen", 3), ("o1", "ink", 1)]
    orders.append(("o2", "pad", 2))
    sent = [("o1", "pen", 3), ("o2", "pad", 1)]
    assert unmatched_order_lines(orders, sent) == ["o1:ink", "o2:pad"]
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0525 - P0530)
    "P0525": {
        "domain": "Matrix & Grid Operations",
        "task": "Sums of each anti-diagonal of a rectangular matrix",
        "category": "Nested loop only",
        "code": '''def anti_diagonal_sums(matrix: list[list[int]]) -> list[int]:
    rows, cols = len(matrix), len(matrix[0])
    sums = [0] * (rows + cols - 1)
    for r in range(rows):
        for c in range(cols):
            sums[r + c] += matrix[r][c]
    return sums

if __name__ == "__main__":
    assert anti_diagonal_sums([[1, 2, 3], [4, 5, 6]]) == [1, 6, 8, 6]
    assert anti_diagonal_sums([[7]]) == [7]
'''
    },
    "P0526": {
        "domain": "Searching and Sorting",
        "task": "Positions where a short pattern list occurs inside a longer list",
        "category": "Nested loop only",
        "code": '''def find_sublist_positions(haystack: list[int], pattern: list[int]) -> list[int]:
    positions = []
    width = len(pattern)
    start = 0
    while start + width <= len(haystack) and width:
        offset = 0
        while offset < width and haystack[start + offset] == pattern[offset]:
            offset += 1
        if offset == width:
            positions.append(start)
        start += 1
    return positions

if __name__ == "__main__":
    assert find_sublist_positions([1, 2, 1, 2, 1], [1, 2, 1]) == [0, 2]
    assert find_sublist_positions([3, 4], [5]) == []
    assert find_sublist_positions([3, 4], []) == []
'''
    },
    "P0527": {
        "domain": "Numerical Computation",
        "task": "Perfect numbers up to a limit using a divisor-sum sieve",
        "category": "Nested loop only",
        "code": '''def perfect_numbers_upto(limit: int) -> list[int]:
    sums = [0] * (limit + 1)
    for d in range(1, limit + 1):
        for multiple in range(2 * d, limit + 1, d):
            sums[multiple] += d
    return [n for n in range(2, limit + 1) if sums[n] == n]

if __name__ == "__main__":
    assert perfect_numbers_upto(30) == [6, 28]
    assert perfect_numbers_upto(5) == []
'''
    },
    "P0528": {
        "domain": "Searching and Sorting",
        "task": "Closest pool value for each query by linear scan",
        "category": "Nested loop only",
        "code": '''def nearest_values(pool: list[int], queries: list[int]) -> list[int]:
    answers = []
    for q in queries:
        best = pool[0]
        for candidate in pool:
            if abs(candidate - q) < abs(best - q):
                best = candidate
        answers.append(best)
    return answers

if __name__ == "__main__":
    assert nearest_values([1, 8, 15], [7, 12, 0]) == [8, 15, 1]
'''
    },
    "P0529": {
        "domain": "Data Aggregation and Statistics",
        "task": "Maximum of every fixed-width sliding window by direct scan",
        "category": "Nested loop only",
        "code": '''def window_maxima(series: list[float], width: int) -> list[float]:
    result = []
    for start in range(len(series) - width + 1):
        top = series[start]
        for offset in range(1, width):
            top = max(top, series[start + offset])
        result.append(top)
    return result

if __name__ == "__main__":
    assert window_maxima([1, 3, 2, 5, 4], 2) == [3, 3, 5, 5]
    assert window_maxima([1, 3, 2], 3) == [3]
'''
    },
    "P0530": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Invert a key-to-values mapping into value-to-keys",
        "category": "Nested loop only",
        "code": '''def invert_multimap(mapping: dict[str, list[str]]) -> dict[str, list[str]]:
    inverted = {}
    for key, values in mapping.items():
        for value in values:
            if key not in inverted.get(value, []):
                inverted.setdefault(value, []).append(key)
    pairs = sorted(inverted.items())
    return {v: sorted(ks) for v, ks in pairs}

if __name__ == "__main__":
    data = {"b": ["x"], "a": ["x", "y", "x"]}
    assert invert_multimap(data) == {"x": ["a", "b"], "y": ["a"]}
'''
    },

    # 4. NONE (6 programs: P0531 - P0536)
    "P0531": {
        "domain": "Numerical Computation",
        "task": "Reduce an integer ratio to lowest terms with a positive sign",
        "category": "None",
        "code": '''from math import gcd

def reduce_ratio(parts: list[int]) -> list[int]:
    if not parts or all(p == 0 for p in parts):
        return list(parts)
    common = 0
    for value in parts:
        common = gcd(common, abs(value))
    sign = -1 if all(p <= 0 for p in parts) else 1
    return [sign * p // common for p in parts]

if __name__ == "__main__":
    assert reduce_ratio([4, 6, 10]) == [2, 3, 5]
    assert reduce_ratio([-2, -4]) == [1, 2]
    assert reduce_ratio([0, 0]) == [0, 0]
'''
    },
    "P0532": {
        "domain": "String Processing & Text Analysis",
        "task": "Convert a snake_case identifier into title words keeping acronyms",
        "category": "None",
        "code": '''def snake_to_title(name: str, keep_upper: set[str]) -> str:
    words = [w for w in name.strip("_").split("_") if w]
    titled = []
    for word in words:
        upper = word.upper()
        if upper in keep_upper:
            titled.append(upper)
        else:
            titled.append(word.capitalize())
    return " ".join(titled)

if __name__ == "__main__":
    assert snake_to_title("_http_status_code", {"HTTP"}) == "HTTP Status Code"
    assert snake_to_title("max__value", set()) == "Max Value"
'''
    },
    "P0533": {
        "domain": "Graph or Tree Traversal",
        "task": "Lowest common ancestor of two nodes from a parent map",
        "category": "None",
        "code": '''def lowest_common_ancestor(parent: dict[str, str], a: str, b: str) -> str:
    ancestors = set()
    node = a
    while node:
        ancestors.add(node)
        node = parent.get(node, "")
    node = b
    while node and node not in ancestors:
        node = parent.get(node, "")
    return node

if __name__ == "__main__":
    parent = {"b": "a", "c": "a", "d": "b", "e": "b"}
    assert lowest_common_ancestor(parent, "d", "e") == "b"
    assert lowest_common_ancestor(parent, "d", "c") == "a"
    assert lowest_common_ancestor(parent, "d", "x") == ""
'''
    },
    "P0534": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Split a list into fixed-size tuples padding the last one",
        "category": "None",
        "code": '''def chunk_with_padding(items: list, size: int, filler=None) -> list[tuple]:
    if size <= 0:
        raise ValueError("size must be positive")
    chunks = []
    for start in range(0, len(items), size):
        piece = list(items[start:start + size])
        piece.extend([filler] * (size - len(piece)))
        chunks.append(tuple(piece))
    return chunks

if __name__ == "__main__":
    assert chunk_with_padding([1, 2, 3, 4, 5], 2, 0) == [(1, 2), (3, 4), (5, 0)]
    assert chunk_with_padding([], 3) == []
'''
    },
    "P0535": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Added, removed and changed keys between two dictionaries",
        "category": "None",
        "code": '''def dict_changes(old: dict, new: dict) -> tuple[list, list, list]:
    added = sorted(k for k in new if k not in old)
    removed = sorted(k for k in old if k not in new)
    shared = [k for k in old if k in new]
    changed = sorted(k for k in shared if old[k] != new[k])
    return added, removed, changed

if __name__ == "__main__":
    before = {"a": 1, "b": 2, "c": 3}
    after = {"b": 2, "c": 4, "d": 5}
    assert dict_changes(before, after) == (["d"], ["a"], ["c"])
'''
    },
    "P0536": {
        "domain": "Data Aggregation and Statistics",
        "task": "Median absolute deviation of a list of values",
        "category": "None",
        "code": '''def middle_value(ordered: list[float]) -> float:
    mid = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2

def median_spread(values: list[float]) -> float:
    if not values:
        raise ValueError("values must not be empty")
    center = middle_value(sorted(values))
    deviations = sorted(abs(v - center) for v in values)
    return middle_value(deviations)

if __name__ == "__main__":
    assert median_spread([1, 1, 2, 2, 4, 6, 9]) == 1
    assert median_spread([3, 5]) == 1.0
'''
    },

    # 5. LONG STATEMENT ONLY (4 programs: P0537 - P0540)
    "P0537": {
        "domain": "Numerical Computation",
        "task": "Future value of a principal with yearly deposits at a fixed rate",
        "category": "Long statement only",
        "code": '''def future_value_with_deposits(principal: float, rate: float, years: int, deposit: float) -> float:
    if rate == 0:
        return principal + deposit * years
    growth = (1 + rate) ** years
    total = principal * growth + deposit * (growth - 1) / rate * (1 + rate)
    return round(total, 2)

if __name__ == "__main__":
    assert future_value_with_deposits(1000, 0.0, 5, 100) == 1500
    assert future_value_with_deposits(1000, 0.1, 2, 100) == 1441.0
'''
    },
    "P0538": {
        "domain": "Data Aggregation and Statistics",
        "task": "Weighted final course score from quizzes, exams and project",
        "category": "Long statement only",
        "code": '''def course_final_score(quizzes: list[float], midterm: float, final: float, project: float) -> float:
    quiz_avg = sum(quizzes) / len(quizzes) if quizzes else 0.0
    return round(quiz_avg * 0.15 + midterm * 0.25 + final * 0.4 + project * 0.2, 1)

if __name__ == "__main__":
    assert abs(course_final_score([80, 100], 60, 80, 90) - 78.5) < 0.06
    assert course_final_score([], 0, 0, 0) == 0.0
'''
    },
    "P0539": {
        "domain": "Inventory and Record Management",
        "task": "Stock valuation net of damage with a handling fee on costly lots",
        "category": "Long statement only",
        "code": '''def stock_valuation(lots: list[tuple[int, float, float]]) -> float:
    value = 0.0
    for qty, unit_cost, damage_rate in lots:
        value += qty * unit_cost * (1 - damage_rate) + qty * 0.15 * (unit_cost > 100)
    return round(value, 2)

if __name__ == "__main__":
    lots = [(10, 50.0, 0.1), (2, 200.0, 0.0)]
    assert stock_valuation(lots) == 850.3
    assert stock_valuation([]) == 0.0
'''
    },
    "P0540": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Rotating daily staff rota with a fixed number per day",
        "category": "Long statement only",
        "code": '''def build_rota(staff: list[str], days: int, per_day: int) -> list[list[str]]:
    rota = []
    for day in range(days):
        start = (day * per_day) % len(staff)
        rota.append([staff[(start + k) % len(staff)] for k in range(per_day)])
    return rota

if __name__ == "__main__":
    assert build_rota(["a", "b", "c"], 2, 2) == [["a", "b"], ["c", "a"]]
    assert build_rota(["a"], 1, 1) == [["a"]]
'''
    },

    # 6. LONG STATEMENT AND NESTED LOOP (4 programs: P0541 - P0544)
    "P0541": {
        "domain": "Matrix & Grid Operations",
        "task": "Five-point box blur of the interior cells of an image grid",
        "category": "Long statement and nested loop",
        "code": '''def box_blur_interior(img: list[list[float]]) -> list[list[float]]:
    out = [row[:] for row in img]
    for r in range(1, len(img) - 1):
        for c in range(1, len(img[0]) - 1):
            out[r][c] = (img[r - 1][c] + img[r + 1][c] + img[r][c - 1] + img[r][c + 1] + img[r][c]) / 5
    return out

if __name__ == "__main__":
    img = [[0.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 0.0]]
    assert box_blur_interior(img)[1][1] == 2.0
    assert box_blur_interior(img)[0][0] == 0.0
'''
    },
    "P0542": {
        "domain": "Graph or Tree Traversal",
        "task": "PageRank scores by fixed-round power iteration",
        "category": "Long statement and nested loop",
        "code": '''def page_rank_scores(links: dict[str, list[str]], rounds: int = 20, damping: float = 0.85) -> dict[str, float]:
    nodes = sorted(links)
    rank = {n: 1 / len(nodes) for n in nodes}
    for _ in range(rounds):
        fresh = {}
        for node in nodes:
            incoming = [src for src in nodes if node in links[src]]
            fresh[node] = (1 - damping) / len(nodes) + damping * sum(rank[s] / len(links[s]) for s in incoming)
        rank = fresh
    return {n: round(r, 3) for n, r in rank.items()}

if __name__ == "__main__":
    assert page_rank_scores({"a": ["b"], "b": ["a"]}) == {"a": 0.5, "b": 0.5}
    links = {"a": ["b", "c"], "b": ["c"], "c": ["a"]}
    scores = page_rank_scores(links)
    assert abs(sum(scores.values()) - 1.0) < 0.01
    assert scores["c"] > scores["b"]
'''
    },
    "P0543": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Horizontal range of projectiles by stepping until they land",
        "category": "Long statement and nested loop",
        "code": '''def simulate_projectiles(launches: list[tuple[float, float]], steps: int, dt: float) -> list[float]:
    ranges = []
    for vx, vy in launches:
        x, y, t = 0.0, 0.0, 0
        while y >= 0.0 and t < steps:
            x += vx * dt
            y = y + vy * dt - 0.5 * 9.81 * dt * dt - 0.5 * 9.81 * dt * dt * (2 * t)
            t += 1
        ranges.append(round(x, 2))
    return ranges

if __name__ == "__main__":
    launches = [(10.0, 0.0), (5.0, 9.0)]
    assert simulate_projectiles(launches, 100, 0.1) == [1.0, 9.5]
'''
    },
    "P0544": {
        "domain": "Searching and Sorting",
        "task": "League table order by points then goal difference using bubble passes",
        "category": "Long statement and nested loop",
        "code": '''def league_table_order(teams: list[tuple[str, int, int, int]]) -> list[str]:
    order = list(teams)
    for end in range(len(order) - 1, 0, -1):
        for i in range(end):
            a, b = order[i], order[i + 1]
            score_gap = (b[1] * 3 + b[2]) * 100 + b[3] - (a[1] * 3 + a[2]) * 100 - a[3]
            if score_gap > 0:
                order[i], order[i + 1] = b, a
    return [team[0] for team in order]

if __name__ == "__main__":
    teams = [("ash", 2, 1, 3), ("elm", 3, 0, 1)]
    teams.append(("oak", 2, 1, 5))
    assert league_table_order(teams) == ["elm", "oak", "ash"]
'''
    },

    # 7. ALL THREE TARGET ISSUES (3 programs: P0545 - P0547)
    "P0545": {
        "domain": "Graph or Tree Traversal",
        "task": "Single-source shortest costs with Bellman-Ford and cycle detection",
        "category": "All three target issues",
        "code": '''def bellman_ford_costs(edges: list[tuple[str, str, int]], nodes: list[str], source: str) -> dict[str, float]:
    cost = {n: float("inf") for n in nodes}
    cost[source] = 0
    for _ in range(len(nodes) - 1):
        for u, v, w in edges:
            if cost[u] != float("inf") and cost[u] + w < cost[v] and v != source:
                cost[v] = cost[u] + w
    for u, v, w in edges:
        candidate_cost_through_edge = cost[u] + w if cost[u] != float("inf") else float("inf")
        if candidate_cost_through_edge < cost[v]:
            raise ValueError("negative cycle")
    return cost

if __name__ == "__main__":
    edges = [("a", "b", 4), ("a", "c", 1), ("c", "b", 2)]
    edges.append(("b", "d", 1))
    costs = bellman_ford_costs(edges, ["a", "b", "c", "d"], "a")
    assert costs == {"a": 0, "b": 3, "c": 1, "d": 4}
'''
    },
    "P0546": {
        "domain": "Matrix & Grid Operations",
        "task": "Matrix product computed only where a mask allows, skipping zeros",
        "category": "All three target issues",
        "code": '''def masked_matrix_product(a: list[list[float]], b: list[list[float]], mask: list[list[int]]) -> list[list[float]]:
    n, m, p = len(a), len(b), len(b[0])
    out = [[0.0] * p for _ in range(n)]
    for i in range(n):
        for j in range(p):
            if mask[i][j] == 0:
                continue
            for k in range(m):
                if a[i][k] != 0 and b[k][j] != 0 and abs(a[i][k] * b[k][j]) > 1e-12:
                    out[i][j] = out[i][j] + a[i][k] * b[k][j] * mask[i][j] / max(1, mask[i][j])
    return out

if __name__ == "__main__":
    a = [[1, 2], [3, 4]]
    b = [[5, 6], [7, 8]]
    mask = [[1, 0], [1, 1]]
    assert masked_matrix_product(a, b, mask) == [[19, 0.0], [43, 50]]
'''
    },
    "P0547": {
        "domain": "String Processing & Text Analysis",
        "task": "Report word n-grams repeated across sentences, ignoring stopword edges",
        "category": "All three target issues",
        "code": '''def repeated_phrase_report(sentences: list[str], n: int, stopwords: set[str]) -> list[str]:
    counts = {}
    for sentence in sentences:
        words = sentence.lower().split()
        for i in range(len(words) - n + 1):
            gram = words[i:i + n]
            if gram[0] not in stopwords and gram[-1] not in stopwords and len(set(gram)) == n:
                key = " ".join(gram)
                counts[key] = counts.get(key, 0) + 1
    report = [f"{phrase} x{count}" for phrase, count in sorted(counts.items()) if count > 1]
    return report

if __name__ == "__main__":
    text = ["the red fox runs", "a red fox sleeps"]
    text.append("red fox red fox")
    assert repeated_phrase_report(text, 2, {"the", "a"}) == ["red fox x4"]
'''
    },

    # 8. LONG STATEMENT AND COMPLEX CONDITIONAL (3 programs: P0548 - P0550)
    "P0548": {
        "domain": "Inventory and Record Management",
        "task": "Invoice total with member coupon discounts and tax",
        "category": "Long statement and complex conditional",
        "code": '''def invoice_total(subtotal: float, customer: dict, coupon: str) -> float:
    member = customer.get("member", False)
    if member and subtotal >= 100 and coupon == "SAVE10":
        discount = 0.1
    elif coupon == "SAVE5":
        discount = 0.05
    else:
        discount = 0.0
    total = subtotal - subtotal * discount + subtotal * (1 - discount) * customer["tax_rate"]
    return round(total, 2)

if __name__ == "__main__":
    shopper = {"member": True, "tax_rate": 0.2}
    assert invoice_total(200, shopper, "SAVE10") == 216.0
    assert invoice_total(50, shopper, "SAVE5") == 57.0
'''
    },
    "P0549": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Batch job priority score with a boost for long-waiting short jobs",
        "category": "Long statement and complex conditional",
        "code": '''def job_priority(job: dict, now: int) -> float:
    if job.get("paused"):
        return 0.0
    waited = now - job["submitted"]
    score = job["base"] * 2 + waited * 0.5 + job.get("boost", 0) * 3 - job["est_minutes"] * 0.1
    if waited > 60 and job["est_minutes"] < 10 and not job.get("batch", False):
        score += 25
    return round(score, 1)

if __name__ == "__main__":
    job = {"submitted": 0, "base": 5, "est_minutes": 5}
    assert job_priority(job, 100) == 84.5
    assert job_priority({"paused": True}, 100) == 0.0
'''
    },
    "P0550": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Thermostat action from a humidity-adjusted feels-like temperature",
        "category": "Long statement and complex conditional",
        "code": '''def thermostat_action(temp: float, target: float, humidity: float, occupied: bool) -> tuple[str, float]:
    feels_like = temp - 0.55 * (1 - humidity / 100) * (temp - 14.5) + 0.1 * (humidity - 50)
    if occupied and feels_like > target + 1 and humidity < 70:
        return "cool", round(feels_like, 1)
    if occupied and (feels_like < target - 1 or temp < 16):
        return "heat", round(feels_like, 1)
    return "hold", round(feels_like, 1)

if __name__ == "__main__":
    assert thermostat_action(30.0, 22.0, 40.0, True)[0] == "cool"
    assert thermostat_action(18.0, 22.0, 50.0, True)[0] == "heat"
    assert thermostat_action(25.0, 22.0, 50.0, False)[0] == "hold"
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 11",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v11.0-expansion",
        "programs": BATCH11_PROGRAMS,
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