"""
build_corpus.py
Writes the Batch 8 (P0351-P0400) programs into program_corpus/programs and
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

BATCH8_PROGRAMS = {
    # 1. NONE (8 programs: P0351 - P0358)
    "P0351": {
        "domain": "Numerical Computation",
        "task": "Digital root of a non-negative integer by repeated digit summation",
        "category": "None",
        "code": '''def digital_root_value(n: int) -> int:
    if n < 0:
        raise ValueError("n must be non-negative")
    total = n
    while total >= 10:
        total = sum(int(digit) for digit in str(total))
    return total

if __name__ == "__main__":
    assert digital_root_value(0) == 0
    assert digital_root_value(9875) == 2
    assert digital_root_value(38) == 2
'''
    },
    "P0352": {
        "domain": "String Processing & Text Analysis",
        "task": "Count vowels and consonants among the letters of a phrase",
        "category": "None",
        "code": '''def count_vowel_consonant(text: str) -> tuple[int, int]:
    vowels = 0
    consonants = 0
    for ch in text.lower():
        if not ch.isalpha():
            continue
        if ch in "aeiou":
            vowels += 1
        else:
            consonants += 1
    return vowels, consonants

if __name__ == "__main__":
    assert count_vowel_consonant("Hello, World!") == (3, 7)
    assert count_vowel_consonant("123") == (0, 0)
'''
    },
    "P0353": {
        "domain": "Searching and Sorting",
        "task": "Exponential search for a target in a sorted list",
        "category": "None",
        "code": '''def exponential_search_index(items: list[int], target: int) -> int:
    if not items:
        return -1
    bound = 1
    while bound < len(items) and items[bound] < target:
        bound *= 2
    low = bound // 2
    high = min(bound, len(items) - 1)
    while low <= high:
        mid = (low + high) // 2
        if items[mid] == target:
            return mid
        if items[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1

if __name__ == "__main__":
    data = [1, 3, 5, 7, 9, 11, 13, 15, 17]
    assert exponential_search_index(data, 13) == 6
    assert exponential_search_index(data, 4) == -1
    assert exponential_search_index([], 4) == -1
'''
    },
    "P0354": {
        "domain": "Data Aggregation and Statistics",
        "task": "Statistical mode of integer observations with smallest-value tie break",
        "category": "None",
        "code": '''def smallest_mode(values: list[int]) -> int:
    if not values:
        raise ValueError("values must not be empty")
    counts: dict[int, int] = {}
    for value in values:
        counts[value] = counts.get(value, 0) + 1
    best_value = min(counts)
    for value, count in counts.items():
        if count > counts[best_value]:
            best_value = value
        elif count == counts[best_value] and value < best_value:
            best_value = value
    return best_value

if __name__ == "__main__":
    assert smallest_mode([4, 1, 2, 2, 4, 3]) == 2
    assert smallest_mode([7]) == 7
'''
    },
    "P0355": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Rotate a list to the right by k positions",
        "category": "None",
        "code": '''def rotate_right_by(items: list[int], k: int) -> list[int]:
    if not items:
        return []
    shift = k % len(items)
    if shift == 0:
        return list(items)
    return items[-shift:] + items[:-shift]

if __name__ == "__main__":
    assert rotate_right_by([1, 2, 3, 4, 5], 2) == [4, 5, 1, 2, 3]
    assert rotate_right_by([1, 2, 3], 3) == [1, 2, 3]
    assert rotate_right_by([], 4) == []
'''
    },
    "P0356": {
        "domain": "Graph or Tree Traversal",
        "task": "Count connected components of an undirected graph with union-find",
        "category": "None",
        "code": '''def uf_find_root(parent: dict[str, str], node: str) -> str:
    while parent[node] != node:
        parent[node] = parent[parent[node]]
        node = parent[node]
    return node

def count_union_components(nodes: list[str], edges: list[tuple[str, str]]) -> int:
    parent = {node: node for node in nodes}
    for a, b in edges:
        root_a = uf_find_root(parent, a)
        root_b = uf_find_root(parent, b)
        if root_a != root_b:
            parent[root_a] = root_b
    return len({uf_find_root(parent, n) for n in nodes})

if __name__ == "__main__":
    assert count_union_components(["a", "b", "c", "d"], [("a", "b"), ("c", "d")]) == 2
    assert count_union_components(["x"], []) == 1
'''
    },
    "P0357": {
        "domain": "Inventory and Record Management",
        "task": "Straight-line depreciation book values of a fixed asset",
        "category": "None",
        "code": '''def straight_line_schedule(cost: float, salvage: float, years: int) -> list[float]:
    if years <= 0:
        raise ValueError("years must be positive")
    annual = (cost - salvage) / years
    book_values = []
    value = cost
    for _ in range(years):
        value -= annual
        book_values.append(round(value, 2))
    return book_values

if __name__ == "__main__":
    assert straight_line_schedule(1000.0, 100.0, 3) == [700.0, 400.0, 100.0]
'''
    },
    "P0358": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Minimum number of meeting rooms for overlapping intervals using a heap",
        "category": "None",
        "code": '''import heapq

def min_meeting_rooms(intervals: list[tuple[int, int]]) -> int:
    ends: list[int] = []
    for start, end in sorted(intervals):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)

if __name__ == "__main__":
    assert min_meeting_rooms([(0, 30), (5, 10), (15, 20)]) == 2
    assert min_meeting_rooms([(1, 2), (2, 3)]) == 1
    assert min_meeting_rooms([]) == 0
'''
    },

    # 2. LONG STATEMENT ONLY (6 programs: P0359 - P0364)
    "P0359": {
        "domain": "Numerical Computation",
        "task": "Body surface area by the Mosteller and DuBois formulas",
        "category": "Long statement only",
        "code": '''import math

def body_surface_areas(height_cm: float, weight_kg: float) -> tuple[float, float]:
    mosteller_m2 = math.sqrt(height_cm * weight_kg / 3600.0)
    dubois_m2 = 0.007184 * (weight_kg ** 0.425) * (height_cm ** 0.725)
    return round(mosteller_m2, 3), round(dubois_m2, 3)

if __name__ == "__main__":
    mosteller, dubois = body_surface_areas(180.0, 80.0)
    assert mosteller == 2.0 and 1.9 < dubois < 2.1
'''
    },
    "P0360": {
        "domain": "Data Aggregation and Statistics",
        "task": "Sharpe and Sortino ratios from periodic portfolio returns",
        "category": "Long statement only",
        "code": '''import math

def sharpe_sortino_ratios(returns: list[float], risk_free: float) -> tuple[float, float]:
    n = len(returns)
    if n < 2:
        raise ValueError("need at least two returns")
    excess = [r - risk_free for r in returns]
    mean_excess = sum(excess) / n
    total_sd = math.sqrt(sum((e - mean_excess) ** 2 for e in excess) / (n - 1))
    downside_sd = math.sqrt(sum(min(0.0, e) ** 2 for e in excess) / n)
    sharpe = mean_excess / total_sd if total_sd > 0 else 0.0
    sortino = mean_excess / downside_sd if downside_sd > 0 else 0.0
    return round(sharpe, 4), round(sortino, 4)

if __name__ == "__main__":
    sharpe, sortino = sharpe_sortino_ratios([0.1, -0.05, 0.2, 0.0], 0.0)
    assert 0.5 < sharpe < 0.6 and sortino == 2.5
'''
    },
    "P0361": {
        "domain": "String Processing & Text Analysis",
        "task": "Gunning fog readability index from sentence and syllable-heavy word counts",
        "category": "Long statement only",
        "code": '''def gunning_fog_index(text: str) -> float:
    sentences = max(1, text.count(".") + text.count("!") + text.count("?"))
    words = [w.strip(".,!?;:").lower() for w in text.split() if w.strip(".,!?;:")]
    complex_words = sum(1 for w in words if sum(1 for ch in w if ch in "aeiouy") >= 3)
    fog = 0.4 * ((len(words) / sentences) + 100.0 * (complex_words / max(1, len(words))))
    return round(fog, 2)

if __name__ == "__main__":
    assert gunning_fog_index("The cat sat. It was happy.") == 1.2
'''
    },
    "P0362": {
        "domain": "Inventory and Record Management",
        "task": "Annual carrying cost of average inventory from capital, storage and obsolescence rates",
        "category": "Long statement only",
        "code": '''def annual_carrying_cost(order_qty: float, safety_stock: float, unit_cost: float, capital_rate: float, storage_rate: float, obsolescence_rate: float) -> float:
    average_units = order_qty / 2.0 + safety_stock
    carrying_rate = capital_rate + storage_rate + obsolescence_rate
    annual_cost = average_units * unit_cost * carrying_rate
    return round(annual_cost, 2)

if __name__ == "__main__":
    assert annual_carrying_cost(200.0, 50.0, 10.0, 0.1, 0.05, 0.05) == 300.0
'''
    },
    "P0363": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Free-fall velocity and distance under linear air drag",
        "category": "Long statement only",
        "code": '''import math

def drag_fall_state(mass_kg: float, drag_coeff: float, time_s: float, gravity: float = 9.81) -> tuple[float, float]:
    terminal_velocity = mass_kg * gravity / drag_coeff
    decay = math.exp(-drag_coeff * time_s / mass_kg)
    velocity = terminal_velocity * (1.0 - decay)
    distance = terminal_velocity * time_s - terminal_velocity * (mass_kg / drag_coeff) * (1.0 - decay)
    return round(velocity, 3), round(distance, 3)

if __name__ == "__main__":
    assert drag_fall_state(80.0, 10.0, 0.0) == (0.0, 0.0)
    assert drag_fall_state(80.0, 10.0, 1000.0)[0] == 78.48
'''
    },
    "P0364": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Little's law cycle time and excess work-in-process for a production line",
        "category": "Long statement only",
        "code": '''def littles_law_metrics(throughput_per_hr: float, wip_units: float, target_cycle_hr: float) -> tuple[float, float]:
    if throughput_per_hr <= 0.0:
        raise ValueError("throughput must be positive")
    cycle_time_hr = wip_units / throughput_per_hr
    wip_needed_for_target = throughput_per_hr * target_cycle_hr
    excess_wip_fraction = (wip_units - wip_needed_for_target) / max(1.0, wip_needed_for_target)
    return round(cycle_time_hr, 3), round(excess_wip_fraction, 3)

if __name__ == "__main__":
    assert littles_law_metrics(10.0, 50.0, 4.0) == (5.0, 0.25)
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0365 - P0370)
    "P0365": {
        "domain": "Searching and Sorting",
        "task": "Comb sort with a shrinking comparison gap",
        "category": "Nested loop only",
        "code": '''def comb_sort_values(values: list[int]) -> list[int]:
    arr = list(values)
    gap = len(arr)
    swapped = True
    while gap > 1 or swapped:
        gap = max(1, int(gap / 1.3))
        swapped = False
        for i in range(len(arr) - gap):
            if arr[i] > arr[i + gap]:
                arr[i], arr[i + gap] = arr[i + gap], arr[i]
                swapped = True
    return arr

if __name__ == "__main__":
    assert comb_sort_values([8, 4, 1, 56, 3, -44, 23]) == [-44, 1, 3, 4, 8, 23, 56]
    assert comb_sort_values([]) == []
'''
    },
    "P0366": {
        "domain": "Matrix & Grid Operations",
        "task": "Spiral order traversal of a rectangular matrix",
        "category": "Nested loop only",
        "code": '''def spiral_order(matrix: list[list[int]]) -> list[int]:
    result = []
    if not matrix:
        return result
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    while top <= bottom and left <= right:
        for c in range(left, right + 1):
            result.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):
            result.append(matrix[r][right])
        right -= 1
        if top <= bottom:
            for c in range(right, left - 1, -1):
                result.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:
            for r in range(bottom, top - 1, -1):
                result.append(matrix[r][left])
            left += 1
    return result

if __name__ == "__main__":
    assert spiral_order([[1, 2, 3], [4, 5, 6], [7, 8, 9]]) == [1, 2, 3, 6, 9, 8, 7, 4, 5]
    assert spiral_order([]) == []
'''
    },
    "P0367": {
        "domain": "String Processing & Text Analysis",
        "task": "Longest common prefix shared by every word in a list",
        "category": "Nested loop only",
        "code": '''def longest_shared_prefix(words: list[str]) -> str:
    if not words:
        return ""
    prefix = words[0]
    for word in words[1:]:
        length = 0
        for a, b in zip(prefix, word):
            if a != b:
                break
            length += 1
        prefix = prefix[:length]
    return prefix

if __name__ == "__main__":
    assert longest_shared_prefix(["flower", "flow", "flight"]) == "fl"
    assert longest_shared_prefix(["dog", "car"]) == ""
'''
    },
    "P0368": {
        "domain": "Graph or Tree Traversal",
        "task": "Dijkstra single-source shortest path distances with a binary heap",
        "category": "Nested loop only",
        "code": '''import heapq

def dijkstra_distances(graph: dict[str, list[tuple[str, float]]], source: str) -> dict[str, float]:
    best = {source: 0.0}
    heap = [(0.0, source)]
    while heap:
        dist, node = heapq.heappop(heap)
        if dist > best.get(node, float("inf")):
            continue
        for neighbor, weight in graph.get(node, []):
            candidate = dist + weight
            if candidate < best.get(neighbor, float("inf")):
                best[neighbor] = candidate
                heapq.heappush(heap, (candidate, neighbor))
    return best

if __name__ == "__main__":
    g = {"a": [("b", 4.0), ("c", 1.0)], "c": [("b", 2.0)]}
    assert dijkstra_distances(g, "a") == {"a": 0.0, "b": 3.0, "c": 1.0}
'''
    },
    "P0369": {
        "domain": "Data Aggregation and Statistics",
        "task": "Kendall tau-a rank correlation from concordant and discordant pairs",
        "category": "Nested loop only",
        "code": '''def kendall_tau_a(xs: list[float], ys: list[float]) -> float:
    n = len(xs)
    if n < 2:
        raise ValueError("need at least two pairs")
    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            sign = (xs[i] - xs[j]) * (ys[i] - ys[j])
            if sign > 0:
                concordant += 1
            elif sign < 0:
                discordant += 1
    pairs = n * (n - 1) / 2
    return round((concordant - discordant) / pairs, 4)

if __name__ == "__main__":
    assert kendall_tau_a([1, 2, 3], [1, 2, 3]) == 1.0
    assert kendall_tau_a([1, 2, 3], [3, 2, 1]) == -1.0
'''
    },
    "P0370": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Langton's ant walk on a toroidal grid and final black-cell count",
        "category": "Nested loop only",
        "code": '''def langtons_ant_black_cells(size: int, steps: int) -> int:
    grid = [[0] * size for _ in range(size)]
    row, col = size // 2, size // 2
    heading = 0
    moves = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    for _ in range(steps):
        if grid[row][col] == 0:
            heading = (heading + 1) % 4
        else:
            heading = (heading - 1) % 4
        grid[row][col] ^= 1
        dr, dc = moves[heading]
        row = (row + dr) % size
        col = (col + dc) % size
    black = 0
    for line in grid:
        for cell in line:
            black += cell
    return black

if __name__ == "__main__":
    assert langtons_ant_black_cells(5, 0) == 0
    assert langtons_ant_black_cells(5, 4) == 4
'''
    },

    # 4. COMPLEX CONDITIONAL ONLY (6 programs: P0371 - P0376)
    "P0371": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate hexadecimal colour codes in short, long and alpha forms",
        "category": "Complex conditional only",
        "code": '''def is_hex_color(code: str) -> bool:
    if not code.startswith("#") or len(code) not in (4, 7, 9):
        return False
    for ch in code[1:]:
        if not ("0" <= ch <= "9" or "a" <= ch.lower() <= "f"):
            return False
    return True

if __name__ == "__main__":
    assert is_hex_color("#1a2B3c") is True
    assert is_hex_color("#fff") is True
    assert is_hex_color("#12345g") is False
    assert is_hex_color("123456") is False
'''
    },
    "P0372": {
        "domain": "Numerical Computation",
        "task": "Check whether three integer points form a right triangle",
        "category": "Complex conditional only",
        "code": '''def is_right_triangle(p: tuple[int, int], q: tuple[int, int], r: tuple[int, int]) -> bool:
    a = (p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2
    b = (q[0] - r[0]) ** 2 + (q[1] - r[1]) ** 2
    c = (r[0] - p[0]) ** 2 + (r[1] - p[1]) ** 2
    if a == 0 or b == 0 or c == 0:
        return False
    return a + b == c or b + c == a or a + c == b

if __name__ == "__main__":
    assert is_right_triangle((0, 0), (3, 0), (0, 4)) is True
    assert is_right_triangle((0, 0), (2, 1), (5, 3)) is False
    assert is_right_triangle((1, 1), (1, 1), (2, 2)) is False
'''
    },
    "P0373": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Approve a remote-work day against team coverage and probation rules",
        "category": "Complex conditional only",
        "code": '''def approve_remote_day(on_site_count: int, team_size: int, on_probation: bool, has_client_meeting: bool, weekday: int) -> bool:
    if on_probation or has_client_meeting or weekday not in range(5):
        return False
    remaining = on_site_count - 1
    if remaining < 2 or remaining * 2 < team_size:
        return False
    return True

if __name__ == "__main__":
    assert approve_remote_day(6, 8, False, False, 2) is True
    assert approve_remote_day(2, 8, False, False, 2) is False
    assert approve_remote_day(6, 8, True, False, 2) is False
'''
    },
    "P0374": {
        "domain": "Inventory and Record Management",
        "task": "Decide whether a library loan can be renewed by its borrower",
        "category": "Complex conditional only",
        "code": '''def can_renew_loan(loan: dict[str, int], fines_due: float, item_type: str) -> tuple[bool, str]:
    limits = {"book": 3, "dvd": 1, "journal": 0}
    allowed = limits.get(item_type, 0)
    blocked = fines_due > 10.0 and loan["late"] > 0
    if loan["renewed"] >= allowed or loan["holds"] > 0 or blocked:
        return False, "denied"
    new_due = loan["due"] + (21 if item_type == "book" else 7)
    return True, f"day {new_due}"

if __name__ == "__main__":
    loan = {"renewed": 1, "holds": 0, "late": 0, "due": 10}
    assert can_renew_loan(loan, 0.0, "book") == (True, "day 31")
    assert can_renew_loan(loan, 0.0, "dvd") == (False, "denied")
    assert can_renew_loan(loan, 0.0, "journal") == (False, "denied")
'''
    },
    "P0375": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Next traffic-light phase from elapsed time, pedestrian requests and emergency override",
        "category": "Complex conditional only",
        "code": '''def next_signal_phase(phase: str, elapsed_s: int, ped_button: bool, emergency: bool, queue_len: int) -> str:
    if emergency:
        return "ALL_RED"
    if phase == "GREEN" and (elapsed_s >= 45 or (ped_button and elapsed_s >= 15)):
        return "YELLOW"
    if phase == "YELLOW" and elapsed_s >= 4:
        return "RED"
    if phase == "RED" and elapsed_s >= 30 and queue_len > 0:
        return "GREEN"
    return phase

if __name__ == "__main__":
    assert next_signal_phase("GREEN", 20, True, False, 0) == "YELLOW"
    assert next_signal_phase("GREEN", 20, False, False, 0) == "GREEN"
    assert next_signal_phase("RED", 35, False, False, 3) == "GREEN"
    assert next_signal_phase("RED", 5, False, True, 3) == "ALL_RED"
'''
    },
    "P0376": {
        "domain": "Matrix & Grid Operations",
        "task": "Check that a tic-tac-toe board is reachable under alternating legal play",
        "category": "Complex conditional only",
        "code": '''ROWS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
COLS = ((0, 3, 6), (1, 4, 7), (2, 5, 8))
DIAGS = ((0, 4, 8), (2, 4, 6))

def count_wins(board: str, mark: str) -> int:
    wins = 0
    for a, b, c in ROWS + COLS + DIAGS:
        if board[a] == mark and board[b] == mark and board[c] == mark:
            wins += 1
    return wins

def is_reachable_tictactoe(board: str) -> bool:
    x_count = board.count("X")
    o_count = board.count("O")
    if len(board) != 9 or x_count < o_count or x_count > o_count + 1:
        return False
    x_wins = count_wins(board, "X")
    o_wins = count_wins(board, "O")
    if x_wins and o_wins:
        return False
    if x_wins and x_count != o_count + 1:
        return False
    if o_wins and x_count != o_count:
        return False
    return True

if __name__ == "__main__":
    assert is_reachable_tictactoe("XXXOO....") is True
    assert is_reachable_tictactoe("XXXOOO...") is False
    assert is_reachable_tictactoe("XX.......") is False
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (6 programs: P0377 - P0382)
    "P0377": {
        "domain": "Numerical Computation",
        "task": "Power iteration estimate of the dominant eigenvalue of a square matrix",
        "category": "Long statement and nested loop",
        "code": '''import math

def power_iteration_dominant(matrix: list[list[float]], iterations: int) -> float:
    n = len(matrix)
    vector = [1.0] * n
    eigenvalue = 0.0
    for _ in range(iterations):
        product = [0.0] * n
        for i in range(n):
            product[i] = sum(matrix[i][j] * vector[j] for j in range(n))
        norm = math.sqrt(sum(value * value for value in product))
        vector = [value / norm for value in product]
        eigenvalue = sum(vector[i] * sum(matrix[i][j] * vector[j] for j in range(n)) for i in range(n))
    return round(eigenvalue, 4)

if __name__ == "__main__":
    assert power_iteration_dominant([[2.0, 0.0], [0.0, 1.0]], 50) == 2.0
'''
    },
    "P0378": {
        "domain": "Data Aggregation and Statistics",
        "task": "Inverse-distance weighted k-nearest-neighbour regression for query points",
        "category": "Long statement and nested loop",
        "code": '''import math

def knn_inverse_distance_predict(train: list[tuple[float, float, float]], queries: list[tuple[float, float]], k: int) -> list[float]:
    predictions = []
    for qx, qy in queries:
        scored = []
        for tx, ty, target in train:
            distance = math.hypot(qx - tx, qy - ty)
            scored.append((distance, target))
        nearest = sorted(scored)[:k]
        weighted_sum = sum(target / (distance + 1e-9) for distance, target in nearest)
        weight_total = sum(1.0 / (distance + 1e-9) for distance, _ in nearest)
        predictions.append(round(weighted_sum / weight_total, 3))
    return predictions

if __name__ == "__main__":
    train = [(0.0, 0.0, 10.0), (10.0, 10.0, 20.0)]
    assert knn_inverse_distance_predict(train, [(0.0, 0.0)], 2) == [10.0]
'''
    },
    "P0379": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Explicit finite-difference heat conduction along a rod with fixed ends",
        "category": "Long statement and nested loop",
        "code": '''def heat_rod_profile(initial: list[float], alpha: float, dx: float, dt: float, steps: int) -> list[float]:
    temps = list(initial)
    ratio = alpha * dt / (dx * dx)
    for _ in range(steps):
        updated = list(temps)
        for i in range(1, len(temps) - 1):
            updated[i] = temps[i] + ratio * (temps[i - 1] - 2.0 * temps[i] + temps[i + 1])
        temps = updated
    return [round(value, 4) for value in temps]

if __name__ == "__main__":
    assert heat_rod_profile([0.0, 100.0, 0.0], 1.0, 1.0, 0.25, 1) == [0.0, 50.0, 0.0]
'''
    },
    "P0380": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Machine utilisation percentages per shift from job runtime logs",
        "category": "Long statement and nested loop",
        "code": '''def shift_utilization_matrix(logs: dict[str, list[list[float]]], shift_hours: float) -> dict[str, list[float]]:
    utilization = {}
    for machine, shifts in logs.items():
        ratios = []
        for runtimes in shifts:
            busy_hours = sum(runtimes)
            ratios.append(round(min(1.0, busy_hours / shift_hours) * 100.0, 1))
        utilization[machine] = ratios
    return utilization

if __name__ == "__main__":
    assert shift_utilization_matrix({"M1": [[2.0, 2.0], [8.0, 1.0]]}, 8.0) == {"M1": [50.0, 100.0]}
'''
    },
    "P0381": {
        "domain": "Inventory and Record Management",
        "task": "Freshness-weighted stock value across warehouse aisles and bins",
        "category": "Long statement and nested loop",
        "code": '''def shelf_life_stock_value(aisles: list[list[tuple[int, float, int, int]]]) -> float:
    total_value = 0.0
    for aisle in aisles:
        for units, unit_price, days_left, shelf_life in aisle:
            freshness = max(0.0, days_left / shelf_life)
            total_value += units * unit_price * (0.5 + 0.5 * freshness) * (1.0 if days_left > 0 else 0.0)
    return round(total_value, 2)

if __name__ == "__main__":
    assert shelf_life_stock_value([[(10, 2.0, 5, 10)], [(4, 3.0, 0, 10)]]) == 15.0
'''
    },
    "P0382": {
        "domain": "Matrix & Grid Operations",
        "task": "Gamma correction with linear contrast stretch of a grayscale image",
        "category": "Long statement and nested loop",
        "code": '''def gamma_contrast_adjust(image: list[list[int]], gamma: float, low: int, high: int) -> list[list[int]]:
    adjusted = []
    for row in image:
        new_row = []
        for pixel in row:
            stretched = min(1.0, max(0.0, (pixel - low) / max(1, high - low)))
            new_row.append(int(round(255.0 * stretched ** gamma)))
        adjusted.append(new_row)
    return adjusted

if __name__ == "__main__":
    assert gamma_contrast_adjust([[0, 128, 255]], 1.0, 0, 255) == [[0, 128, 255]]
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0383 - P0388)
    "P0383": {
        "domain": "Numerical Computation",
        "task": "Apparent temperature from wind chill or heat index by weather regime",
        "category": "Long statement and complex conditional",
        "code": '''def apparent_temperature_c(temp_c: float, wind_kmh: float, humidity_pct: float) -> float:
    if temp_c <= 10.0 and wind_kmh > 4.8 and humidity_pct >= 0.0:
        wind_chill = 13.12 + 0.6215 * temp_c - 11.37 * wind_kmh ** 0.16 + 0.3965 * temp_c * wind_kmh ** 0.16
        return round(wind_chill, 1)
    if temp_c >= 27.0 and humidity_pct >= 40.0 and humidity_pct <= 100.0:
        heat_index = temp_c + 0.5555 * (6.11 * 2.718281828 ** (5417.753 * (1 / 273.16 - 1 / (temp_c + 273.15))) * humidity_pct / 100.0 - 10.0)
        return round(heat_index, 1)
    return round(temp_c, 1)

if __name__ == "__main__":
    assert apparent_temperature_c(20.0, 10.0, 50.0) == 20.0
    assert apparent_temperature_c(0.0, 20.0, 50.0) == -5.2
    assert apparent_temperature_c(35.0, 10.0, 60.0) > 35.0
'''
    },
    "P0384": {
        "domain": "Data Aggregation and Statistics",
        "task": "Final course letter grade with exam curve, attendance penalty and plagiarism override",
        "category": "Long statement and complex conditional",
        "code": '''def final_course_grade(exam: float, coursework: float, attendance_pct: float, plagiarism_flag: bool, curve_points: float) -> str:
    if plagiarism_flag or attendance_pct < 50.0 or exam < 0.0 or coursework < 0.0:
        return "F"
    weighted_score = 0.6 * min(100.0, exam + curve_points) + 0.4 * coursework - (5.0 if attendance_pct < 75.0 else 0.0)
    if weighted_score >= 85.0:
        return "A"
    if weighted_score >= 70.0:
        return "B"
    if weighted_score >= 55.0:
        return "C"
    return "F"

if __name__ == "__main__":
    assert final_course_grade(90.0, 80.0, 90.0, False, 0.0) == "A"
    assert final_course_grade(60.0, 60.0, 60.0, False, 0.0) == "C"
    assert final_course_grade(90.0, 90.0, 40.0, False, 0.0) == "F"
'''
    },
    "P0385": {
        "domain": "String Processing & Text Analysis",
        "task": "Parse and range-check a compact ISO-8601 date-time string",
        "category": "Long statement and complex conditional",
        "code": '''def parse_iso_datetime(stamp: str) -> tuple[int, int, int, int, int]:
    if len(stamp) != 16 or stamp[4] != "-" or stamp[7] != "-" or stamp[10] != "T" or stamp[13] != ":":
        raise ValueError("expected YYYY-MM-DDTHH:MM")
    year, month, day = int(stamp[0:4]), int(stamp[5:7]), int(stamp[8:10])
    hour, minute = int(stamp[11:13]), int(stamp[14:16])
    if not (1 <= month <= 12) or not (1 <= day <= 31) or hour > 23 or minute > 59:
        raise ValueError("date-time field out of range")
    return year, month, day, hour, minute

if __name__ == "__main__":
    assert parse_iso_datetime("2026-10-25T14:15") == (2026, 10, 25, 14, 15)
'''
    },
    "P0386": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Greenhouse roof vent opening and misting decision from climate sensors",
        "category": "Long statement and complex conditional",
        "code": '''def greenhouse_actuators(temp_c: float, humidity_pct: float, co2_ppm: float, raining: bool, wind_ms: float) -> tuple[int, bool]:
    vent_pct = int(max(0.0, min(100.0, (temp_c - 24.0) * 12.5 + (co2_ppm - 800.0) * 0.05)))
    if raining or wind_ms > 12.0 or temp_c < 10.0:
        vent_pct = 0
    misting = humidity_pct < 55.0 and temp_c > 28.0 and not raining
    return vent_pct, misting

if __name__ == "__main__":
    assert greenhouse_actuators(32.0, 40.0, 800.0, False, 3.0) == (100, True)
    assert greenhouse_actuators(32.0, 40.0, 800.0, True, 3.0) == (0, False)
'''
    },
    "P0387": {
        "domain": "Inventory and Record Management",
        "task": "Pallet rack beam load check with seismic derating and impact damage",
        "category": "Long statement and complex conditional",
        "code": '''def rack_beam_load_ok(load_kg: float, beam_rating_kg: float, seismic_zone: int, damaged: bool, inspection_days: int) -> tuple[bool, float]:
    seismic_factor = 1.0 if seismic_zone <= 1 else 0.85 if seismic_zone == 2 else 0.7
    derated_capacity_kg = beam_rating_kg * seismic_factor * (0.5 if damaged else 1.0)
    if damaged and inspection_days > 30 or load_kg > derated_capacity_kg or load_kg < 0.0:
        return False, round(derated_capacity_kg, 1)
    return True, round(derated_capacity_kg, 1)

if __name__ == "__main__":
    assert rack_beam_load_ok(800.0, 1000.0, 1, False, 0) == (True, 1000.0)
    assert rack_beam_load_ok(800.0, 1000.0, 3, False, 0) == (False, 700.0)
'''
    },
    "P0388": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Nurse shift pay with night, holiday and overtime multipliers under fatigue limits",
        "category": "Long statement and complex conditional",
        "code": '''def nurse_shift_pay(hours: float, base_rate: float, night_shift: bool, consecutive_days: int, holiday: bool) -> float:
    if hours <= 0.0 or hours > 16.0 or consecutive_days > 6:
        raise ValueError("shift violates fatigue limits")
    overtime_hours = max(0.0, hours - 8.0)
    multiplier = (1.25 if night_shift else 1.0) * (2.0 if holiday else 1.0)
    shift_pay = base_rate * multiplier * (min(hours, 8.0) + 1.5 * overtime_hours)
    return round(shift_pay, 2)

if __name__ == "__main__":
    assert nurse_shift_pay(10.0, 20.0, False, 1, False) == 220.0
    assert nurse_shift_pay(8.0, 20.0, True, 1, True) == 400.0
'''
    },

    # 7. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0389 - P0394)
    "P0389": {
        "domain": "Matrix & Grid Operations",
        "task": "Count islands of land cells with iterative flood fill",
        "category": "Nested loop and complex conditional",
        "code": '''def count_land_islands(grid: list[list[int]]) -> int:
    rows, cols = len(grid), len(grid[0])
    seen = set()
    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] != 1 or (r, c) in seen:
                continue
            islands += 1
            stack = [(r, c)]
            seen.add((r, c))
            while stack:
                cr, cc = stack.pop()
                for nr, nc in ((cr + 1, cc), (cr - 1, cc), (cr, cc + 1), (cr, cc - 1)):
                    inside = 0 <= nr < rows and 0 <= nc < cols
                    if inside and grid[nr][nc] == 1 and (nr, nc) not in seen:
                        seen.add((nr, nc))
                        stack.append((nr, nc))
    return islands

if __name__ == "__main__":
    assert count_land_islands([[1, 1, 0], [0, 0, 1], [1, 0, 1]]) == 3
'''
    },
    "P0390": {
        "domain": "Graph or Tree Traversal",
        "task": "Suggest friends-of-friends who share at least two interests",
        "category": "Nested loop and complex conditional",
        "code": '''def suggest_friends(friends: dict[str, set[str]], interests: dict[str, set[str]]) -> list[tuple[str, str]]:
    suggestions = []
    for user, circle in friends.items():
        for friend in circle:
            for candidate in friends.get(friend, set()):
                shared = interests[user] & interests[candidate]
                if candidate != user and candidate not in circle and len(shared) >= 2:
                    suggestions.append((user, candidate))
    return sorted(set(suggestions))

if __name__ == "__main__":
    f = {"a": {"b"}, "b": {"a", "c"}, "c": {"b"}}
    tags = {"a": {"x", "y"}, "b": set(), "c": {"x", "y", "z"}}
    assert suggest_friends(f, tags) == [("a", "c"), ("c", "a")]
'''
    },
    "P0391": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Detect roster shifts that violate the minimum rest gap between consecutive shifts",
        "category": "Nested loop and complex conditional",
        "code": '''def find_rest_violations(roster: dict[str, list[tuple[int, int]]], min_rest: int) -> list[tuple[str, int]]:
    violations = []
    for nurse, shifts in roster.items():
        ordered = sorted(shifts)
        for k in range(1, len(ordered)):
            prev_end = ordered[k - 1][1]
            start, end = ordered[k]
            gap = start - prev_end
            if gap < min_rest and end > start and prev_end > 0:
                violations.append((nurse, k))
    return violations

if __name__ == "__main__":
    roster = {"N1": [(0, 8), (12, 20), (40, 48)]}
    assert find_rest_violations(roster, 10) == [("N1", 1)]
'''
    },
    "P0392": {
        "domain": "String Processing & Text Analysis",
        "task": "Find ordered word pairs whose concatenation is a palindrome",
        "category": "Nested loop and complex conditional",
        "code": '''def palindrome_join_pairs(words: list[str], min_len: int) -> list[tuple[int, int]]:
    pairs = []
    for i, first in enumerate(words):
        for j, second in enumerate(words):
            joined = first + second
            if i != j and len(joined) >= min_len and joined == joined[::-1]:
                pairs.append((i, j))
    return pairs

if __name__ == "__main__":
    assert palindrome_join_pairs(["ab", "ba", "x"], 2) == [(0, 1), (1, 0)]
'''
    },
    "P0393": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Single update step of the Brian's Brain three-state cellular automaton",
        "category": "Nested loop and complex conditional",
        "code": '''def brians_brain_step(grid: list[list[int]]) -> list[list[int]]:
    rows, cols = len(grid), len(grid[0])
    nxt = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            state = grid[r][c]
            if state == 1:
                nxt[r][c] = 2
                continue
            if state == 2:
                continue
            firing = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    rr, cc = r + dr, c + dc
                    if (dr or dc) and 0 <= rr < rows and 0 <= cc < cols:
                        firing += grid[rr][cc] == 1
            if firing == 2:
                nxt[r][c] = 1
    return nxt

if __name__ == "__main__":
    assert brians_brain_step([[1, 1, 0], [0, 0, 0]]) == [[2, 2, 0], [1, 1, 0]]
'''
    },
    "P0394": {
        "domain": "Inventory and Record Management",
        "task": "Three-way match of goods receipts to supplier invoices within price tolerance",
        "category": "Nested loop and complex conditional",
        "code": '''def three_way_match(receipts: list[tuple[str, str, int]], invoices: list[tuple[str, str, int, float]], unit_prices: dict[str, float]) -> list[str]:
    matched = []
    for po, sku, qty in receipts:
        for inv_id, inv_sku, inv_qty, inv_price in invoices:
            expected = unit_prices[sku]
            price_ok = abs(inv_price - expected) <= 0.02 * expected
            if inv_sku == sku and inv_qty == qty and price_ok:
                matched.append(inv_id)
                break
    return matched

if __name__ == "__main__":
    receipts = [("PO1", "A", 10)]
    invoices = [("I1", "A", 10, 5.05), ("I2", "A", 10, 5.0)]
    assert three_way_match(receipts, invoices, {"A": 5.0}) == ["I1"]
'''
    },

    # 8. ALL THREE TARGET ISSUES (6 programs: P0395 - P0400)
    "P0395": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Herd migration across a habitat-quality grid with barriers and crowding",
        "category": "All three target issues",
        "code": '''def migrate_herds(grid: list[list[float]], herds: list[tuple[int, int, int]], barriers: set[tuple[int, int]], steps: int) -> list[tuple[int, int, int]]:
    rows, cols = len(grid), len(grid[0])
    current = list(herds)
    for _ in range(steps):
        moved = []
        for r, c, size in current:
            best_r, best_c, best_score = r, c, grid[r][c]
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols and (nr, nc) not in barriers:
                    crowding_penalty = 0.01 * size * sum(1 for hr, hc, _ in current if (hr, hc) == (nr, nc))
                    score = grid[nr][nc] - crowding_penalty
                    if score > best_score:
                        best_r, best_c, best_score = nr, nc, score
            moved.append((best_r, best_c, size))
        current = moved
    return current

if __name__ == "__main__":
    habitat = [[0.1, 0.9], [0.2, 0.3]]
    assert migrate_herds(habitat, [(0, 0, 10)], set(), 2) == [(0, 1, 10)]
'''
    },
    "P0396": {
        "domain": "Matrix & Grid Operations",
        "task": "Detect urban heat island hotspots from surface temperature and vegetation grids",
        "category": "All three target issues",
        "code": '''def urban_heat_hotspots(lst: list[list[float]], ndvi: list[list[float]], built_up: list[list[bool]]) -> list[tuple[int, int, float]]:
    rows, cols = len(lst), len(lst[0])
    hotspots = []
    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            neighborhood = [lst[r + dr][c + dc] for dr in (-1, 0, 1) for dc in (-1, 0, 1) if dr or dc]
            anomaly = lst[r][c] - sum(neighborhood) / len(neighborhood)
            if anomaly > 2.0 and ndvi[r][c] < 0.2 and built_up[r][c]:
                hotspots.append((r, c, round(anomaly, 2)))
    return hotspots

if __name__ == "__main__":
    temps = [[30.0, 30.0, 30.0], [30.0, 40.0, 30.0], [30.0, 30.0, 30.0]]
    veg = [[0.1] * 3 for _ in range(3)]
    urban = [[True] * 3 for _ in range(3)]
    assert urban_heat_hotspots(temps, veg, urban) == [(1, 1, 10.0)]
'''
    },
    "P0397": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Assign exam invigilators to rooms under subject conflict and workload caps",
        "category": "All three target issues",
        "code": '''def assign_invigilators(rooms: list[tuple[str, str, int]], staff: list[tuple[str, str, int]]) -> tuple[dict[str, list[str]], list[str]]:
    load = {name: 0 for name, _, _ in staff}
    plan = {}
    for room, subject, needed in sorted(rooms, key=lambda item: -item[2]):
        chosen = []
        for name, own_subject, cap in staff:
            if len(chosen) < needed and own_subject != subject and load[name] < cap:
                chosen.append(name)
                load[name] += 1
        plan[room] = chosen
    unmet_rooms = [room for room, _, needed in rooms if len(plan[room]) < needed]
    return plan, unmet_rooms

if __name__ == "__main__":
    rooms = [("R1", "math", 2), ("R2", "bio", 1)]
    staff = [("A", "math", 2), ("B", "bio", 2), ("C", "chem", 1)]
    assert assign_invigilators(rooms, staff) == ({"R1": ["B", "C"], "R2": ["A"]}, [])
'''
    },
    "P0398": {
        "domain": "Inventory and Record Management",
        "task": "Audit grain silo moisture and depth-sensor temperatures for spoilage risk",
        "category": "All three target issues",
        "code": '''def audit_grain_silos(silos: list[dict], moisture_limit: float) -> list[tuple[str, int]]:
    alerts = []
    for silo in silos:
        for depth, readings in enumerate(silo["sensor_columns"]):
            hottest = max(readings)
            spoilage_risk = 0.6 * max(0.0, silo["moisture_pct"] - moisture_limit) + 0.4 * max(0.0, hottest - silo["ambient_c"]) / 5.0
            if spoilage_risk > 1.0 and not silo["aeration_on"] and silo["fill_pct"] > 10.0:
                alerts.append((silo["id"], depth))
    return alerts

if __name__ == "__main__":
    silo = {"id": "S1", "sensor_columns": [[20.0, 22.0], [20.0, 35.0]], "moisture_pct": 15.0, "ambient_c": 20.0, "aeration_on": False, "fill_pct": 80.0}
    assert audit_grain_silos([silo], 14.0) == [("S1", 1)]
'''
    },
    "P0399": {
        "domain": "Numerical Computation",
        "task": "Grid search of launch speed and angle that clear a target height window",
        "category": "All three target issues",
        "code": '''import math

def search_launch_solutions(speeds: list[float], angles_deg: list[float], target_x: float, window_y: tuple[float, float], gravity: float = 9.81) -> list[tuple[float, float]]:
    solutions = []
    for speed in speeds:
        for angle in angles_deg:
            theta = math.radians(angle)
            vx = speed * math.cos(theta)
            if vx <= 0.0:
                continue
            flight_t = target_x / vx
            height_at_target = speed * math.sin(theta) * flight_t - 0.5 * gravity * flight_t ** 2
            if window_y[0] <= height_at_target <= window_y[1] and angle < 80.0:
                solutions.append((speed, angle))
    return solutions

if __name__ == "__main__":
    assert search_launch_solutions([20.0], [45.0, 85.0], 10.0, (0.0, 20.0)) == [(20.0, 45.0)]
'''
    },
    "P0400": {
        "domain": "Data Aggregation and Statistics",
        "task": "Flag loan vintages with weighted early-delinquency drift across monthly cohorts",
        "category": "All three target issues",
        "code": '''def flag_delinquent_vintages(vintages: dict[str, list[list[int]]], balances: dict[str, float], threshold: float) -> list[str]:
    flagged = []
    for vintage, months in vintages.items():
        worst_rate = 0.0
        for month_index, buckets in enumerate(months):
            current, dpd30, dpd60, dpd90 = buckets
            total = max(1, current + dpd30 + dpd60 + dpd90)
            weighted_delinquency = (0.2 * dpd30 + 0.5 * dpd60 + 1.0 * dpd90) / total * (1.0 + 0.05 * month_index)
            worst_rate = max(worst_rate, weighted_delinquency)
        if worst_rate >= threshold and balances.get(vintage, 0.0) > 1e5 and len(months) >= 3:
            flagged.append(vintage)
    return flagged

if __name__ == "__main__":
    early = [[100, 0, 0, 0], [90, 5, 3, 2], [80, 10, 5, 5]]
    clean = [[100, 0, 0, 0]] * 3
    books = {"2025Q1": early, "2025Q2": clean}
    sizes = {"2025Q1": 2e5, "2025Q2": 2e5}
    assert flag_delinquent_vintages(books, sizes, 0.05) == ["2025Q1"]
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 8",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v8.0-expansion",
        "programs": BATCH8_PROGRAMS,
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