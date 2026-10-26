"""
build_corpus.py
Writes the Batch 13 (P0601-P0650) programs into program_corpus/programs and
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

BATCH13_PROGRAMS = {
    # 1. COMPLEX CONDITIONAL ONLY (15 programs: P0601 - P0615)
    "P0601": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Parking exit gate rule from ticket, payment time and plate flag",
        "category": "Complex conditional only",
        "code": '''def gate_should_open(has_ticket, paid, minutes_since_payment, plate_flagged):
    if plate_flagged:
        return False
    if has_ticket and paid and minutes_since_payment <= 15:
        return True
    return False

if __name__ == "__main__":
    assert gate_should_open(True, True, 10, False)
    assert not gate_should_open(True, True, 20, False)
    assert not gate_should_open(True, True, 1, True)
'''
    },
    "P0602": {
        "domain": "Inventory and Record Management",
        "task": "Accept, hold or flag a goods receipt line against its purchase order",
        "category": "Complex conditional only",
        "code": '''def accept_receipt_line(ordered_qty, received_qty, unit_price, invoiced_price, tolerance=0.02):
    over = received_qty - ordered_qty
    price_gap = abs(invoiced_price - unit_price) / unit_price
    if received_qty > 0 and over <= ordered_qty * 0.05 and price_gap <= tolerance:
        return "accept"
    if received_qty == 0:
        return "missing"
    return "hold"

if __name__ == "__main__":
    assert accept_receipt_line(100, 103, 2.0, 2.02) == "accept"
    assert accept_receipt_line(100, 110, 2.0, 2.0) == "hold"
    assert accept_receipt_line(100, 0, 2.0, 2.0) == "missing"
'''
    },
    "P0603": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Whether a nurse may take an on-call slot given hours, rest and seniority",
        "category": "Complex conditional only",
        "code": '''def can_take_on_call(hours_this_week, last_shift_end, slot_start, is_senior, slot_is_icu):
    rest = slot_start - last_shift_end
    if hours_this_week + 12 <= 60 and rest >= 8 and (is_senior or not slot_is_icu):
        return True
    return False

if __name__ == "__main__":
    assert can_take_on_call(40, 0, 10, False, False)
    assert not can_take_on_call(40, 0, 10, False, True)
    assert not can_take_on_call(50, 0, 10, True, True)
'''
    },
    "P0604": {
        "domain": "String Processing & Text Analysis",
        "task": "Check a word can be played from a letter rack and is in the dictionary",
        "category": "Complex conditional only",
        "code": '''from collections import Counter

def playable_word(word, rack, dictionary):
    need = Counter(word.lower())
    have = Counter(rack.lower())
    enough = all(have[ch] >= n for ch, n in need.items())
    if word.lower() in dictionary and enough and 2 <= len(word) <= len(rack):
        return True
    return False

if __name__ == "__main__":
    assert playable_word("cat", "tacx", {"cat"})
    assert not playable_word("cat", "ta", {"cat"})
    assert not playable_word("dog", "godx", {"cat"})
'''
    },
    "P0605": {
        "domain": "Numerical Computation",
        "task": "Integer square root by bisection with a round limit",
        "category": "Complex conditional only",
        "code": '''def bisect_isqrt(n):
    if n < 0:
        raise ValueError("negative input")
    lo, hi = 0, n + 1
    rounds = 0
    while hi - lo > 1 and rounds < 200 and n > 1:
        mid = (lo + hi) // 2
        if mid * mid <= n:
            lo = mid
        else:
            hi = mid
        rounds += 1
    return lo if n > 1 else n

if __name__ == "__main__":
    assert bisect_isqrt(0) == 0
    assert bisect_isqrt(1) == 1
    assert bisect_isqrt(15) == 3
    assert bisect_isqrt(16) == 4
    assert bisect_isqrt(10 ** 12) == 10 ** 6
'''
    },
    "P0606": {
        "domain": "Data Aggregation and Statistics",
        "task": "Grade survey response quality from speed, attention check and straight-lining",
        "category": "Complex conditional only",
        "code": '''def response_quality(answers, seconds_taken, attention_check):
    distinct = len(set(answers))
    if seconds_taken < 30 or attention_check != "blue" or distinct == 1 and len(answers) > 5:
        return "reject"
    if seconds_taken < 60:
        return "review"
    return "accept"

if __name__ == "__main__":
    assert response_quality([3, 3, 3, 3, 3, 3], 100, "blue") == "reject"
    assert response_quality([1, 2, 3], 45, "blue") == "review"
    assert response_quality([1, 2], 90, "blue") == "accept"
    assert response_quality([1], 90, "red") == "reject"
'''
    },
    "P0607": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Numeric settings under a key prefix whose values fall in a range",
        "category": "Complex conditional only",
        "code": '''def select_settings(config, prefix, low, high):
    chosen = {}
    for key in sorted(config):
        value = config[key]
        if key.startswith(prefix) and isinstance(value, (int, float)) and low <= value <= high:
            chosen[key] = value
    return chosen

if __name__ == "__main__":
    cfg = {"net.timeout": 30, "net.retries": 9}
    cfg["net.host"] = "x"
    cfg["ui.size"] = 12
    assert select_settings(cfg, "net.", 1, 30) == {"net.retries": 9, "net.timeout": 30}
    assert select_settings(cfg, "ui.", 1, 10) == {}
'''
    },
    "P0608": {
        "domain": "Searching and Sorting",
        "task": "Lower bound in a sorted list by galloping then binary search",
        "category": "Complex conditional only",
        "code": '''def gallop_lower_bound(values, target):
    bound = 1
    while bound < len(values) and values[bound] < target and bound < 1 << 30:
        bound *= 2
    lo, hi = bound // 2, min(bound, len(values))
    while lo < hi:
        mid = (lo + hi) // 2
        if values[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo

if __name__ == "__main__":
    nums = [1, 3, 5, 7, 9, 11]
    assert gallop_lower_bound(nums, 6) == 3
    assert gallop_lower_bound(nums, 0) == 0
    assert gallop_lower_bound(nums, 12) == 6
    assert gallop_lower_bound([], 5) == 0
'''
    },
    "P0609": {
        "domain": "Graph or Tree Traversal",
        "task": "Height of a binary tree, or -1 when any subtree is unbalanced",
        "category": "Complex conditional only",
        "code": '''def balanced_height(tree, node):
    if node is None:
        return 0
    left, right = tree.get(node, (None, None))
    lh = balanced_height(tree, left)
    rh = balanced_height(tree, right)
    if lh < 0 or rh < 0 or abs(lh - rh) > 1:
        return -1
    return 1 + max(lh, rh)

if __name__ == "__main__":
    tree = {"a": ("b", "c"), "b": ("d", None)}
    assert balanced_height(tree, "a") == 3
    chain = {"a": ("b", None), "b": ("c", None)}
    assert balanced_height(chain, "a") == -1
'''
    },
    "P0610": {
        "domain": "Inventory and Record Management",
        "task": "Refund outcome from purchase age, packaging, receipt and history",
        "category": "Complex conditional only",
        "code": '''def refund_decision(days_since_purchase, opened, receipt, amount, customer_refunds):
    if not receipt and amount > 50:
        return "deny"
    if days_since_purchase <= 30 and not opened and customer_refunds < 5:
        return "full"
    if days_since_purchase <= 60 and customer_refunds < 5:
        return "store_credit"
    return "deny"

if __name__ == "__main__":
    assert refund_decision(10, False, True, 20, 0) == "full"
    assert refund_decision(45, True, True, 20, 0) == "store_credit"
    assert refund_decision(10, False, False, 80, 0) == "deny"
    assert refund_decision(70, False, True, 20, 0) == "deny"
'''
    },
    "P0611": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Next action of a robot vacuum from battery, bin and sensors",
        "category": "Complex conditional only",
        "code": '''def vacuum_next_action(battery, bin_full, dirt_ahead, obstacle_ahead, docked):
    if battery < 15 and not docked:
        return "return_to_dock"
    if bin_full or battery < 15:
        return "wait"
    if dirt_ahead and not obstacle_ahead and battery >= 30:
        return "clean_forward"
    if obstacle_ahead:
        return "turn"
    return "forward"

if __name__ == "__main__":
    assert vacuum_next_action(10, False, False, False, False) == "return_to_dock"
    assert vacuum_next_action(10, False, False, False, True) == "wait"
    assert vacuum_next_action(50, False, True, False, False) == "clean_forward"
    assert vacuum_next_action(50, False, True, True, False) == "turn"
    assert vacuum_next_action(20, False, True, False, False) == "forward"
'''
    },
    "P0612": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Flag a project milestone at risk from workload, team size and blockers",
        "category": "Complex conditional only",
        "code": '''def milestone_at_risk(days_left, tasks_open, avg_task_days, blockers, team_size):
    if team_size <= 0:
        return True
    needed = tasks_open * avg_task_days / team_size
    if needed > days_left or blockers >= 3 or needed > 0.8 * days_left and blockers > 0:
        return True
    return False

if __name__ == "__main__":
    assert not milestone_at_risk(10, 4, 2, 0, 2)
    assert milestone_at_risk(10, 12, 2, 0, 2)
    assert milestone_at_risk(10, 9, 2, 1, 2)
    assert milestone_at_risk(10, 4, 2, 0, 0)
'''
    },
    "P0613": {
        "domain": "String Processing & Text Analysis",
        "task": "Detect a shouted chat message from capital ratio and exclamation",
        "category": "Complex conditional only",
        "code": '''def is_shouting(message):
    letters = [ch for ch in message if ch.isalpha()]
    if not letters:
        return False
    ratio = sum(ch.isupper() for ch in letters) / len(letters)
    if ratio >= 0.8 and len(letters) >= 5 and message.count("!") >= 1:
        return True
    return False

if __name__ == "__main__":
    assert is_shouting("STOP THAT NOW!")
    assert not is_shouting("STOP THAT NOW")
    assert not is_shouting("Hi!")
    assert not is_shouting("123!")
'''
    },
    "P0614": {
        "domain": "Numerical Computation",
        "task": "Validate step size, interval and order for a numerical ODE solver",
        "category": "Complex conditional only",
        "code": '''def valid_step_parameters(h, t0, t_end, order):
    if not isinstance(order, int):
        return False
    if h > 0 and t_end > t0 and h <= (t_end - t0) and 1 <= order <= 4:
        return True
    return False

if __name__ == "__main__":
    assert valid_step_parameters(0.1, 0, 1, 4)
    assert not valid_step_parameters(2, 0, 1, 4)
    assert not valid_step_parameters(0.1, 0, 1, 5)
    assert not valid_step_parameters(0.1, 0, 1, 2.0)
'''
    },
    "P0615": {
        "domain": "Data Aggregation and Statistics",
        "task": "Count readings accumulated before a running total would pass a limit",
        "category": "Complex conditional only",
        "code": '''def readings_until_alarm(readings, limit, max_count):
    total = 0.0
    i = 0
    while i < len(readings) and i < max_count and total + readings[i] <= limit:
        total += readings[i]
        i += 1
    return i, round(total, 2)

if __name__ == "__main__":
    assert readings_until_alarm([2.5, 3.0, 4.0, 1.0], 6.0, 10) == (2, 5.5)
    assert readings_until_alarm([1, 1, 1], 10, 2) == (2, 2.0)
    assert readings_until_alarm([], 5, 5) == (0, 0.0)
'''
    },

    # 2. NESTED LOOP AND COMPLEX CONDITIONAL (15 programs: P0616 - P0630)
    "P0616": {
        "domain": "Matrix & Grid Operations",
        "task": "Clear pixels that have no lit neighbour in their 3x3 window",
        "category": "Nested loop and complex conditional",
        "code": '''def remove_isolated_pixels(img):
    h, w = len(img), len(img[0])
    out = [row[:] for row in img]
    for r in range(h):
        for c in range(w):
            if img[r][c] == 0:
                continue
            neighbours = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = r + dr, c + dc
                    if (dr or dc) and 0 <= rr < h and 0 <= cc < w and img[rr][cc]:
                        neighbours += 1
            if neighbours == 0:
                out[r][c] = 0
    return out

if __name__ == "__main__":
    img = [[1, 0, 0], [0, 0, 0], [0, 1, 1]]
    assert remove_isolated_pixels(img) == [[0, 0, 0], [0, 0, 0], [0, 1, 1]]
'''
    },
    "P0617": {
        "domain": "Matrix & Grid Operations",
        "task": "Index pairs where a square matrix is not symmetric within tolerance",
        "category": "Nested loop and complex conditional",
        "code": '''def asymmetric_pairs(matrix, tol):
    n = len(matrix)
    bad = []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = matrix[i][j], matrix[j][i]
            if a is not None and b is not None and abs(a - b) > tol:
                bad.append((i, j))
    return bad

if __name__ == "__main__":
    m = [[1, 2, 3], [2, 1, None], [3.5, 0, 1]]
    assert asymmetric_pairs(m, 0.1) == [(0, 2)]
    assert asymmetric_pairs(m, 1.0) == []
'''
    },
    "P0618": {
        "domain": "Matrix & Grid Operations",
        "task": "Local peaks reached by steepest-ascent hill climbing from start cells",
        "category": "Nested loop and complex conditional",
        "code": '''def hill_climb_peaks(grid, starts):
    peaks = []
    for r, c in starts:
        moved = True
        while moved:
            moved = False
            best = grid[r][c]
            for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
                if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and grid[nr][nc] > best:
                    best, r, c, moved = grid[nr][nc], nr, nc, True
        peaks.append((r, c))
    return peaks

if __name__ == "__main__":
    grid = [[1, 2, 3], [2, 3, 4], [3, 4, 9]]
    assert hill_climb_peaks(grid, [(0, 0), (2, 2)]) == [(2, 2), (2, 2)]
'''
    },
    "P0619": {
        "domain": "Graph or Tree Traversal",
        "task": "Count start-to-goal paths in a DAG up to a maximum length",
        "category": "Nested loop and complex conditional",
        "code": '''def count_bounded_paths(dag, start, goal, max_len):
    total = 0
    stack = [(start, 0)]
    while stack:
        node, length = stack.pop()
        if node == goal and length > 0:
            total += 1
            continue
        for nxt in dag.get(node, []):
            if length + 1 <= max_len and nxt != start and nxt not in ("", None):
                stack.append((nxt, length + 1))
    return total

if __name__ == "__main__":
    dag = {"s": ["a", "b"], "a": ["t", "b"], "b": ["t"]}
    assert count_bounded_paths(dag, "s", "t", 2) == 2
    assert count_bounded_paths(dag, "s", "t", 3) == 3
'''
    },
    "P0620": {
        "domain": "Graph or Tree Traversal",
        "task": "Two-colour an undirected graph by BFS or report it is not bipartite",
        "category": "Nested loop and complex conditional",
        "code": '''from collections import deque

def two_colour_graph(adj):
    colour = {}
    for start in sorted(adj):
        if start in colour:
            continue
        colour[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nb in adj[node]:
                if nb not in colour:
                    colour[nb] = 1 - colour[node]
                    queue.append(nb)
                elif colour[nb] == colour[node] and nb != node and adj[nb]:
                    return None
    return colour

if __name__ == "__main__":
    square = {"a": ["b", "d"], "b": ["a", "c"]}
    square.update({"c": ["b", "d"], "d": ["c", "a"]})
    assert two_colour_graph(square) == {"a": 0, "b": 1, "d": 1, "c": 0}
    tri = {"x": ["y", "z"], "y": ["x", "z"], "z": ["x", "y"]}
    assert two_colour_graph(tri) is None
'''
    },
    "P0621": {
        "domain": "Searching and Sorting",
        "task": "Pairs of distinct sorted values no further apart than a gap",
        "category": "Nested loop and complex conditional",
        "code": '''def close_pairs(values, max_gap):
    ordered = sorted(values)
    pairs = []
    for i in range(len(ordered)):
        j = i + 1
        while j < len(ordered) and ordered[j] - ordered[i] <= max_gap and ordered[j] != ordered[i]:
            pairs.append((ordered[i], ordered[j]))
            j += 1
    return pairs

if __name__ == "__main__":
    assert close_pairs([1, 4, 2, 9], 2) == [(1, 2), (2, 4)]
    assert close_pairs([], 3) == []
'''
    },
    "P0622": {
        "domain": "Searching and Sorting",
        "task": "Staircase search for several targets in a row and column sorted matrix",
        "category": "Nested loop and complex conditional",
        "code": '''def staircase_search_all(matrix, targets):
    found = {}
    for target in targets:
        r, c = 0, len(matrix[0]) - 1
        found[target] = None
        while r < len(matrix) and c >= 0 and found[target] is None:
            if matrix[r][c] == target:
                found[target] = (r, c)
            elif matrix[r][c] > target:
                c -= 1
            else:
                r += 1
    return found

if __name__ == "__main__":
    m = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    assert staircase_search_all(m, [5, 10]) == {5: (1, 1), 10: None}
'''
    },
    "P0623": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Group cleaned words by first letter skipping banned and short words",
        "category": "Nested loop and complex conditional",
        "code": '''def group_by_initial(lists, banned, min_len):
    groups = {}
    for words in lists:
        for word in words:
            w = word.strip().lower()
            if w and len(w) >= min_len and w not in banned and w not in groups.get(w[0], []):
                groups.setdefault(w[0], []).append(w)
    return groups

if __name__ == "__main__":
    lists = [["Apple", "ant"], ["apple ", "bee", "be"]]
    assert group_by_initial(lists, {"ant"}, 3) == {"a": ["apple"], "b": ["bee"]}
'''
    },
    "P0624": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Indexes of sets contained in another set of the list",
        "category": "Nested loop and complex conditional",
        "code": '''def redundant_sets(sets):
    redundant = []
    for i, small in enumerate(sets):
        for j, big in enumerate(sets):
            if i != j and small <= big and (small != big or i > j):
                redundant.append(i)
                break
    return redundant

if __name__ == "__main__":
    assert redundant_sets([{1, 2}, {1, 2, 3}, {4}, {1, 2}]) == [0, 3]
    assert redundant_sets([{1}, {2}]) == []
'''
    },
    "P0625": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "One predation step where wolves eat sheep sharing their cell",
        "category": "Nested loop and complex conditional",
        "code": '''def predation_step(cells):
    survivors = []
    for row in cells:
        new_row = []
        for animals in row:
            wolves, sheep = animals.count("W"), animals.count("S")
            if wolves > 0 and sheep > 0 and wolves >= sheep // 2:
                new_row.append("W" * wolves)
            else:
                new_row.append(animals)
        survivors.append(new_row)
    return survivors

if __name__ == "__main__":
    cells = [["WS", "SS"], ["W", "SSSW"]]
    assert predation_step(cells) == [["W", "SS"], ["W", "W"]]
'''
    },
    "P0626": {
        "domain": "Inventory and Record Management",
        "task": "Store batches close to expiry that still have stock to discount",
        "category": "Nested loop and complex conditional",
        "code": '''def batches_to_discount(stores, today, window):
    picks = []
    for store, batches in sorted(stores.items()):
        for batch_id, expires, qty in batches:
            days_left = expires - today
            if 0 <= days_left <= window and qty > 0 and not batch_id.startswith("X"):
                picks.append((store, batch_id))
    return picks

if __name__ == "__main__":
    stores = {"s1": [("b1", 12, 5), ("X2", 11, 3)]}
    stores["s2"] = [("b3", 30, 4), ("b4", 10, 0)]
    assert batches_to_discount(stores, 10, 3) == [("s1", "b1")]
'''
    },
    "P0627": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Course pairs booked into the same room in a shared time slot",
        "category": "Nested loop and complex conditional",
        "code": '''def conflicting_courses(courses):
    conflicts = set()
    for name_a, room_a, slots_a in courses:
        for name_b, room_b, slots_b in courses:
            if name_a < name_b and room_a == room_b and set(slots_a) & set(slots_b):
                conflicts.add((name_a, name_b))
    return sorted(conflicts)

if __name__ == "__main__":
    courses = [("algo", "R1", [1, 2]), ("bio", "R1", [2, 3])]
    courses.append(("chem", "R2", [1]))
    assert conflicting_courses(courses) == [("algo", "bio")]
'''
    },
    "P0628": {
        "domain": "String Processing & Text Analysis",
        "task": "Line and position of every word containing a doubled letter",
        "category": "Nested loop and complex conditional",
        "code": '''def doubled_letter_counts(lines, min_len):
    counts = {}
    for number, line in enumerate(lines, start=1):
        words = line.lower().split()
        for position, raw in enumerate(words):
            w = raw.strip(".,;:!?")
            doubled = any(a == b for a, b in zip(w, w[1:]))
            if doubled and len(w) >= min_len and w.isalpha():
                counts.setdefault(w, []).append((number, position))
    return counts

if __name__ == "__main__":
    lines = ["Look at the moon.", "Good food, cool moon"]
    found = doubled_letter_counts(lines, 4)
    assert found["moon"] == [(1, 3), (2, 3)]
    assert sorted(found) == ["cool", "food", "good", "look", "moon"]
'''
    },
    "P0629": {
        "domain": "Numerical Computation",
        "task": "Numbers up to a limit written as a sum of two coprime squares",
        "category": "Nested loop and complex conditional",
        "code": '''from math import gcd

def primitive_two_square_sums(limit):
    results = []
    for n in range(1, limit + 1):
        a = 1
        while a * a * 2 <= n:
            b_sq = n - a * a
            b = int(b_sq ** 0.5)
            if b * b == b_sq and a <= b and gcd(a, b) == 1:
                results.append((n, a, b))
            a += 1
    return results

if __name__ == "__main__":
    assert primitive_two_square_sums(10) == [(2, 1, 1), (5, 1, 2), (10, 1, 3)]
'''
    },
    "P0630": {
        "domain": "Data Aggregation and Statistics",
        "task": "Time steps where every monitored series exceeds its threshold",
        "category": "Nested loop and complex conditional",
        "code": '''def joint_exceedances(series, thresholds):
    length = min(len(values) for values in series.values())
    hits = []
    for t in range(length):
        above = 0
        for name, values in series.items():
            if name in thresholds and values[t] is not None and values[t] > thresholds[name]:
                above += 1
        if above == len(thresholds):
            hits.append(t)
    return hits

if __name__ == "__main__":
    series = {"temp": [30, 35, 36], "hum": [50, 80, None]}
    assert joint_exceedances(series, {"temp": 32, "hum": 70}) == [1]
'''
    },

    # 3. NESTED LOOP ONLY (7 programs: P0631 - P0637)
    "P0631": {
        "domain": "Matrix & Grid Operations",
        "task": "Row sums of the upper triangle of a square matrix",
        "category": "Nested loop only",
        "code": '''def upper_triangle_row_sums(matrix):
    sums = []
    for i, row in enumerate(matrix):
        total = 0
        for j in range(i, len(row)):
            total += row[j]
        sums.append(total)
    return sums

if __name__ == "__main__":
    assert upper_triangle_row_sums([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [6, 11, 9]
'''
    },
    "P0632": {
        "domain": "Graph or Tree Traversal",
        "task": "Nodes of a tree grouped level by level from the root",
        "category": "Nested loop only",
        "code": '''def tree_levels(children, root):
    levels = []
    frontier = [root]
    while frontier:
        levels.append(sorted(frontier))
        nxt = []
        for node in frontier:
            nxt.extend(children.get(node, []))
        frontier = nxt
    return levels

if __name__ == "__main__":
    kids = {"a": ["c", "b"], "b": ["d"]}
    assert tree_levels(kids, "a") == [["a"], ["b", "c"], ["d"]]
'''
    },
    "P0633": {
        "domain": "Searching and Sorting",
        "task": "Start and length of the longest strictly rising run in each list",
        "category": "Nested loop only",
        "code": '''def longest_rising_runs(lists):
    results = []
    for seq in lists:
        best_start, best_len = 0, 0
        start = 0
        for i in range(1, len(seq) + 1):
            if i == len(seq) or seq[i] <= seq[i - 1]:
                if i - start > best_len:
                    best_start, best_len = start, i - start
                start = i
        results.append((best_start, best_len))
    return results

if __name__ == "__main__":
    runs = longest_rising_runs([[1, 2, 3, 1, 2], [5, 4], []])
    assert runs == [(0, 3), (0, 1), (0, 0)]
'''
    },
    "P0634": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Every combination of option values as a list of dictionaries",
        "category": "Nested loop only",
        "code": '''def expand_options(options):
    combos = [{}]
    for key in sorted(options):
        expanded = []
        for combo in combos:
            for value in options[key]:
                expanded.append({**combo, key: value})
        combos = expanded
    return combos

if __name__ == "__main__":
    options = {"size": ["S", "M"], "color": ["red"]}
    combos = expand_options(options)
    assert combos == [{"color": "red", "size": "S"}, {"color": "red", "size": "M"}]
'''
    },
    "P0635": {
        "domain": "String Processing & Text Analysis",
        "task": "Counts of all character n-grams up to a maximum length",
        "category": "Nested loop only",
        "code": '''def char_ngram_profile(text, max_n):
    profile = {}
    cleaned = text.lower()
    for n in range(1, max_n + 1):
        for i in range(len(cleaned) - n + 1):
            gram = cleaned[i:i + n]
            profile[gram] = profile.get(gram, 0) + 1
    return profile

if __name__ == "__main__":
    assert char_ngram_profile("abab", 2) == {"a": 2, "b": 2, "ab": 2, "ba": 1}
'''
    },
    "P0636": {
        "domain": "Numerical Computation",
        "task": "Rows of Pascal's triangle reduced modulo a number",
        "category": "Nested loop only",
        "code": '''def pascal_mod_rows(rows, modulus):
    table = [[1]]
    for n in range(1, rows):
        prev = table[-1]
        row = [1]
        for k in range(1, n):
            row.append((prev[k - 1] + prev[k]) % modulus)
        row.append(1)
        table.append(row)
    return table

if __name__ == "__main__":
    table = pascal_mod_rows(5, 3)
    assert table[3] == [1, 0, 0, 1]
    assert table[4] == [1, 1, 0, 1, 1]
'''
    },
    "P0637": {
        "domain": "Data Aggregation and Statistics",
        "task": "Histogram counts for values over fixed half-open bin edges",
        "category": "Nested loop only",
        "code": '''def bin_counts(values, edges):
    counts = [0] * (len(edges) - 1)
    for v in values:
        for b in range(len(edges) - 1):
            if edges[b] <= v < edges[b + 1]:
                counts[b] += 1
                break
    return counts

if __name__ == "__main__":
    assert bin_counts([1, 2, 5, 7, 10], [0, 3, 6, 10]) == [2, 1, 1]
'''
    },

    # 4. LONG STATEMENT AND NESTED LOOP (7 programs: P0638 - P0644)
    "P0638": {
        "domain": "Matrix & Grid Operations",
        "task": "Upscale a grid to double resolution by averaging corner pixels",
        "category": "Long statement and nested loop",
        "code": '''def upscale_double(img):
    h, w = len(img), len(img[0])
    out = [[0.0] * (2 * w - 1) for _ in range(2 * h - 1)]
    for r in range(2 * h - 1):
        for c in range(2 * w - 1):
            r0, c0 = r // 2, c // 2
            r1, c1 = min(r0 + r % 2, h - 1), min(c0 + c % 2, w - 1)
            out[r][c] = (img[r0][c0] + img[r0][c1] + img[r1][c0] + img[r1][c1]) / 4
    return out

if __name__ == "__main__":
    big = upscale_double([[0, 4], [8, 12]])
    assert big[0][1] == 2.0 and big[1][1] == 6.0 and big[2][2] == 12.0
'''
    },
    "P0639": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Populations after generations of migration, growth and mortality",
        "category": "Long statement and nested loop",
        "code": '''def migrate_populations(pops, rates, growth, mortality, generations):
    current = list(pops)
    for _ in range(generations):
        nxt = [0.0] * len(current)
        for i, size in enumerate(current):
            for j, rate in enumerate(rates[i]):
                nxt[j] = nxt[j] + size * rate * (1 + growth[i]) * (1 - mortality[j])
        current = [round(x, 6) for x in nxt]
    return current

if __name__ == "__main__":
    rates = [[0.5, 0.5], [0, 1]]
    assert migrate_populations([100, 0], rates, [0, 0], [0, 0], 1) == [50, 50]
    assert migrate_populations([100, 0], rates, [0, 0], [0, 0], 2) == [25, 75]
'''
    },
    "P0640": {
        "domain": "Inventory and Record Management",
        "task": "Landed cost per supplier including duty, freight and insurance",
        "category": "Long statement and nested loop",
        "code": '''def landed_costs(shipments):
    totals = {}
    for supplier, lines in shipments.items():
        total = 0.0
        for qty, unit_price, duty_rate, freight in lines:
            total += qty * unit_price * (1 + duty_rate) + freight + qty * unit_price * 0.01
        totals[supplier] = round(total, 2)
    return totals

if __name__ == "__main__":
    assert landed_costs({"acme": [(10, 5.0, 0.1, 2.0)]}) == {"acme": 57.5}
    assert landed_costs({"none": []}) == {"none": 0.0}
'''
    },
    "P0641": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Per-shift machine utilisation net of setup and idle time",
        "category": "Long statement and nested loop",
        "code": '''def machine_utilisation(logs, shift_minutes):
    report = {}
    for machine, shifts in logs.items():
        rates = []
        for run, setup, idle in shifts:
            utilisation = (run - 0.5 * setup) / (shift_minutes - idle) if shift_minutes > idle else 0.0
            rates.append(round(utilisation, 3))
        report[machine] = rates
    return report

if __name__ == "__main__":
    logs = {"m1": [(300, 40, 60), (100, 0, 480)]}
    assert machine_utilisation(logs, 480) == {"m1": [0.667, 0.0]}
'''
    },
    "P0642": {
        "domain": "Graph or Tree Traversal",
        "task": "Normalised weighted degree centrality for each node",
        "category": "Long statement and nested loop",
        "code": '''def weighted_centrality(edges, nodes):
    strength = {n: 0.0 for n in nodes}
    for u, v, w in edges:
        strength[u] += w
        strength[v] += w
    scores = {}
    for n in nodes:
        neighbours = 0
        for u, v, _ in edges:
            neighbours += (u == n) + (v == n)
        scores[n] = round(strength[n] / max(1, neighbours) * neighbours / max(1, len(nodes) - 1), 3)
    return scores

if __name__ == "__main__":
    edges = [("a", "b", 2.0), ("b", "c", 4.0)]
    scores = weighted_centrality(edges, ["a", "b", "c"])
    assert scores == {"a": 1.0, "b": 3.0, "c": 2.0}
'''
    },
    "P0643": {
        "domain": "Searching and Sorting",
        "task": "Bucket sort over the value range with insertion sort per bucket",
        "category": "Long statement and nested loop",
        "code": '''def bucket_sort_range(values, buckets=5):
    if not values:
        return []
    low, high = min(values), max(values)
    bins = [[] for _ in range(buckets)]
    for v in values:
        slot = min(int((v - low) / (high - low) * buckets), buckets - 1) if high > low else 0
        bins[slot].append(v)
    result = []
    for b in bins:
        for i in range(1, len(b)):
            key, j = b[i], i - 1
            while j >= 0 and b[j] > key:
                b[j + 1] = b[j]
                j -= 1
            b[j + 1] = key
        result.extend(b)
    return result

if __name__ == "__main__":
    data = [0.42, 4.2, 1.5, 3.3, 0.1, 2.2, 4.2]
    assert bucket_sort_range(data) == sorted(data)
    assert bucket_sort_range([7, 7]) == [7, 7]
    assert bucket_sort_range([]) == []
'''
    },
    "P0644": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Merge owners' item queues into one list ordered by computed priority",
        "category": "Long statement and nested loop",
        "code": '''def merge_priority_queues(queues):
    merged = []
    for owner, items in sorted(queues.items()):
        for rank, (name, weight) in enumerate(items):
            priority = weight * 10 - rank * 2 + len(owner) * 0.5 - len(name) * 0.1
            merged.append((round(priority, 2), owner, name))
    merged.sort(key=lambda t: (-t[0], t[1], t[2]))
    return [(owner, name) for _, owner, name in merged]

if __name__ == "__main__":
    queues = {"bo": [("x", 1)], "al": [("y", 2), ("zz", 2)]}
    assert merge_priority_queues(queues) == [("al", "y"), ("al", "zz"), ("bo", "x")]
'''
    },

    # 5. LONG STATEMENT ONLY (4 programs: P0645 - P0648)
    "P0645": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Month-end account balance with interest, overdraft rate and low-balance fee",
        "category": "Long statement only",
        "code": '''def month_end_balance(balance, apr, fee, deposits, withdrawals):
    interest = balance * apr / 12 if balance > 0 else balance * (apr + 0.05) / 12
    closing = balance + interest + sum(deposits) - sum(withdrawals) - fee * (balance < 500)
    return round(closing, 2)

if __name__ == "__main__":
    assert month_end_balance(1000, 0.12, 5, [100], [50]) == 1060.0
    assert month_end_balance(-100, 0.12, 5, [], []) == -106.42
'''
    },
    "P0646": {
        "domain": "Inventory and Record Management",
        "task": "Order quantity from economic order size, weekly demand and stock",
        "category": "Long statement only",
        "code": '''from math import sqrt

def order_quantity_plan(annual_demand, order_cost, unit_cost, holding_rate, on_hand):
    eoq = sqrt(2 * annual_demand * order_cost / (unit_cost * holding_rate))
    reorder = max(0, round(eoq) - on_hand + int(annual_demand / 365 * 7) - int(on_hand * 0.1))
    return reorder

if __name__ == "__main__":
    assert order_quantity_plan(1000, 50, 10, 0.2, 100) == 133
    assert order_quantity_plan(1000, 50, 10, 0.2, 5000) == 0
'''
    },
    "P0647": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Expected wait in a call queue from agents, handle time and abandonment",
        "category": "Long statement only",
        "code": '''def estimated_wait_minutes(queue_length, agents, avg_handle_minutes, abandon_rate):
    if agents <= 0:
        return float("inf")
    expected = queue_length * (1 - abandon_rate) * avg_handle_minutes / agents + avg_handle_minutes / 2
    return round(expected, 1)

if __name__ == "__main__":
    assert estimated_wait_minutes(10, 2, 4, 0.1) == 20.0
    assert estimated_wait_minutes(5, 0, 4, 0.0) == float("inf")
'''
    },
    "P0648": {
        "domain": "String Processing & Text Analysis",
        "task": "Reading-ease score from sentence, word and vowel-group counts",
        "category": "Long statement only",
        "code": '''def vowel_group_reading_ease(text):
    sentences = max(1, text.count(".") + text.count("!") + text.count("?"))
    words = text.split()
    syllables = sum(max(1, sum(ch in "aeiouy" for ch in w.lower())) for w in words)
    score = 206.835 - 1.015 * len(words) / sentences - 84.6 * syllables / max(1, len(words))
    return round(score, 1)

if __name__ == "__main__":
    easy = vowel_group_reading_ease("The cat sat. It was fun.")
    jargon = "Unquestionably, organisational duties multiply."
    hard = vowel_group_reading_ease(jargon)
    assert easy > hard
'''
    },

    # 6. ALL THREE TARGET ISSUES (2 programs: P0649 - P0650)
    "P0649": {
        "domain": "Numerical Computation",
        "task": "Weighted sum over a filtered integer grid of index pairs",
        "category": "All three target issues",
        "code": '''def weighted_grid_sum(n, m, threshold):
    total = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if i % 2 == 0 and j % 3 != 0 and i * j <= threshold:
                total += i * j * 0.5 + (i - j) * (i - j) * 0.25 + 1.0 / (i + j)
    return round(total, 4)

if __name__ == "__main__":
    assert weighted_grid_sum(2, 2, 10) == 3.8333
    assert weighted_grid_sum(1, 5, 10) == 0.0
'''
    },
    "P0650": {
        "domain": "Data Aggregation and Statistics",
        "task": "Store weeks whose sales z-score exceeds a limit",
        "category": "All three target issues",
        "code": '''def flag_store_anomalies(sales, z_limit):
    flagged = []
    for store, weeks in sorted(sales.items()):
        mean = sum(weeks) / len(weeks)
        spread = (sum((w - mean) ** 2 for w in weeks) / max(1, len(weeks) - 1)) ** 0.5
        for week, value in enumerate(weeks):
            if spread > 0 and abs(value - mean) / spread > z_limit and value != 0:
                flagged.append((store, week))
    return flagged

if __name__ == "__main__":
    sales = {"s1": [10, 10, 10, 50], "s2": [5, 5]}
    assert flag_store_anomalies(sales, 1.4) == [("s1", 3)]
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 13",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v13.0-expansion",
        "programs": BATCH13_PROGRAMS,
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