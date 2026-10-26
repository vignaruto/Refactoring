"""
build_corpus.py
Writes the Batch 9 (P0401-P0450) programs into program_corpus/programs and
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

BATCH9_PROGRAMS = {
    # 1. NONE (8 programs: P0401 - P0408)
    "P0401": {
        "domain": "Numerical Computation",
        "task": "List Niven (Harshad) numbers divisible by their digit sum up to a limit",
        "category": "None",
        "code": '''def niven_numbers_upto(limit: int) -> list[int]:
    found = []
    for n in range(1, limit + 1):
        digit_sum = sum(int(d) for d in str(n))
        if n % digit_sum == 0:
            found.append(n)
    return found

if __name__ == "__main__":
    assert niven_numbers_upto(12) == [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12]
    assert niven_numbers_upto(0) == []
'''
    },
    "P0402": {
        "domain": "String Processing & Text Analysis",
        "task": "Convert a phrase to headline case keeping minor words lowercase",
        "category": "None",
        "code": '''MINOR_WORDS = {"a", "an", "the", "of", "in", "and", "or"}

def headline_case(text: str) -> str:
    words = text.lower().split()
    result = []
    for index, word in enumerate(words):
        if index > 0 and word in MINOR_WORDS:
            result.append(word)
        else:
            result.append(word.capitalize())
    return " ".join(result)

if __name__ == "__main__":
    assert headline_case("the lord OF the rings") == "The Lord of the Rings"
    assert headline_case("") == ""
'''
    },
    "P0403": {
        "domain": "Searching and Sorting",
        "task": "Jump search over a sorted list using square-root sized blocks",
        "category": "None",
        "code": '''import math

def jump_search_position(items: list[int], target: int) -> int:
    n = len(items)
    step = max(1, int(math.sqrt(n)))
    prev = 0
    while prev < n and items[min(prev + step, n) - 1] < target:
        prev += step
    for i in range(prev, min(prev + step, n)):
        if items[i] == target:
            return i
    return -1

if __name__ == "__main__":
    data = [2, 4, 6, 8, 10, 12, 14, 16, 18]
    assert jump_search_position(data, 14) == 6
    assert jump_search_position(data, 5) == -1
    assert jump_search_position([], 5) == -1
'''
    },
    "P0404": {
        "domain": "Lists, Tuples, Dictionaries, and Sets",
        "task": "Bucket words by length with each bucket sorted alphabetically",
        "category": "None",
        "code": '''def bucket_by_length(words: list[str]) -> dict[int, list[str]]:
    buckets: dict[int, list[str]] = {}
    for word in words:
        buckets.setdefault(len(word), []).append(word)
    for size in buckets:
        buckets[size].sort()
    return dict(sorted(buckets.items()))

if __name__ == "__main__":
    result = bucket_by_length(["kiwi", "fig", "plum", "apple"])
    assert result == {3: ["fig"], 4: ["kiwi", "plum"], 5: ["apple"]}
'''
    },
    "P0405": {
        "domain": "Graph or Tree Traversal",
        "task": "Identify source and sink nodes of a directed edge list",
        "category": "None",
        "code": '''def source_and_sink_nodes(edges: list[tuple[str, str]]) -> tuple[list[str], list[str]]:
    nodes = set()
    has_in = set()
    has_out = set()
    for src, dst in edges:
        nodes.update((src, dst))
        has_out.add(src)
        has_in.add(dst)
    sources = sorted(nodes - has_in)
    sinks = sorted(nodes - has_out)
    return sources, sinks

if __name__ == "__main__":
    edges = [("a", "b"), ("b", "c"), ("d", "c")]
    assert source_and_sink_nodes(edges) == (["a", "d"], ["c"])
'''
    },
    "P0406": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Earliest-due-date job order and its maximum lateness",
        "category": "None",
        "code": '''def edd_max_lateness(jobs: list[tuple[str, int, int]]) -> tuple[list[str], int]:
    order = sorted(jobs, key=lambda job: job[2])
    clock = 0
    worst = 0
    for name, duration, due in order:
        clock += duration
        worst = max(worst, clock - due)
    return [job[0] for job in order], worst

if __name__ == "__main__":
    jobs = [("A", 3, 5), ("B", 2, 3), ("C", 4, 12)]
    assert edd_max_lateness(jobs) == (["B", "A", "C"], 0)
'''
    },
    "P0407": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Thermostat heater state with hysteresis band over temperature readings",
        "category": "None",
        "code": '''def thermostat_hysteresis(readings: list[float], low: float, high: float) -> list[bool]:
    heating = False
    states = []
    for temp in readings:
        if temp < low:
            heating = True
        elif temp > high:
            heating = False
        states.append(heating)
    return states

if __name__ == "__main__":
    temps = [18.0, 19.5, 21.5, 20.0, 18.5]
    assert thermostat_hysteresis(temps, 19.0, 21.0) == [True, True, False, False, True]
'''
    },
    "P0408": {
        "domain": "Inventory and Record Management",
        "task": "Generate the next zero-padded SKU code for a product prefix",
        "category": "None",
        "code": '''def next_sku_code(existing: list[str], prefix: str) -> str:
    highest = 0
    for code in existing:
        if not code.startswith(prefix + "-"):
            continue
        suffix = code[len(prefix) + 1:]
        if suffix.isdigit():
            highest = max(highest, int(suffix))
    return f"{prefix}-{highest + 1:04d}"

if __name__ == "__main__":
    codes = ["TOOL-0007", "TOOL-0012", "PART-0099", "TOOL-x"]
    assert next_sku_code(codes, "TOOL") == "TOOL-0013"
    assert next_sku_code([], "BOLT") == "BOLT-0001"
'''
    },

    # 2. LONG STATEMENT ONLY (6 programs: P0409 - P0414)
    "P0409": {
        "domain": "Numerical Computation",
        "task": "Pendulum period with small-angle and large-amplitude series correction",
        "category": "Long statement only",
        "code": '''import math

def pendulum_periods(length_m: float, amplitude_deg: float, gravity: float = 9.81) -> tuple[float, float]:
    theta = math.radians(amplitude_deg)
    small_angle_period = 2.0 * math.pi * math.sqrt(length_m / gravity)
    corrected_period = small_angle_period * (1.0 + theta ** 2 / 16.0 + 11.0 * theta ** 4 / 3072.0)
    return round(small_angle_period, 4), round(corrected_period, 4)

if __name__ == "__main__":
    small, large = pendulum_periods(1.0, 30.0)
    assert small == 2.0061 and small < large < 2.1
'''
    },
    "P0410": {
        "domain": "Data Aggregation and Statistics",
        "task": "Pearson median skewness and geometric mean of positive observations",
        "category": "Long statement only",
        "code": '''import math
import statistics

def skew_and_geometric_mean(values: list[float]) -> tuple[float, float]:
    if len(values) < 2 or min(values) <= 0:
        raise ValueError("need two or more positive values")
    pearson_median_skew = 3.0 * (statistics.mean(values) - statistics.median(values)) / statistics.stdev(values)
    geometric_mean = math.exp(sum(math.log(v) for v in values) / len(values))
    return round(pearson_median_skew, 4), round(geometric_mean, 4)

if __name__ == "__main__":
    skew, geo = skew_and_geometric_mean([1.0, 2.0, 4.0])
    assert geo == 2.0 and skew > 0
'''
    },
    "P0411": {
        "domain": "String Processing & Text Analysis",
        "task": "Type-token ratio and hapax legomena ratio of a text",
        "category": "Long statement only",
        "code": '''import string

def lexical_richness(text: str) -> tuple[float, float]:
    tokens = [t.strip(string.punctuation).lower() for t in text.split() if t.strip(string.punctuation)]
    if not tokens:
        return 0.0, 0.0
    frequencies = {token: tokens.count(token) for token in set(tokens)}
    hapax_ratio = sum(1 for count in frequencies.values() if count == 1) / len(frequencies)
    return round(len(frequencies) / len(tokens), 4), round(hapax_ratio, 4)

if __name__ == "__main__":
    assert lexical_richness("the cat and the hat") == (0.8, 0.75)
    assert lexical_richness("...") == (0.0, 0.0)
'''
    },
    "P0412": {
        "domain": "Inventory and Record Management",
        "task": "Landed unit cost of an import including freight, insurance, duty and fees",
        "category": "Long statement only",
        "code": '''def landed_unit_cost(unit_price: float, quantity: int, freight: float, duty_rate: float, insurance_rate: float) -> float:
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    goods_value = unit_price * quantity
    customs_value = goods_value + freight + goods_value * insurance_rate
    total_landed = customs_value + customs_value * duty_rate + 0.003464 * customs_value
    return round(total_landed / quantity, 2)

if __name__ == "__main__":
    assert landed_unit_cost(10.0, 100, 50.0, 0.05, 0.01) == 11.17
'''
    },
    "P0413": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Order shop jobs by critical ratio of time remaining to work remaining",
        "category": "Long statement only",
        "code": '''def critical_ratio_order(jobs: list[tuple[str, int, float]], today: int) -> list[tuple[str, float]]:
    ratios = [(name, round((due - today) / max(work_days, 0.5), 3)) for name, due, work_days in jobs]
    return sorted(ratios, key=lambda pair: (pair[1], pair[0]))

if __name__ == "__main__":
    jobs = [("A", 20, 5.0), ("B", 12, 4.0), ("C", 15, 10.0)]
    assert critical_ratio_order(jobs, 10) == [("B", 0.5), ("C", 0.5), ("A", 2.0)]
'''
    },
    "P0414": {
        "domain": "Graph or Tree Traversal",
        "task": "Density and average degree of an undirected simple graph",
        "category": "Long statement only",
        "code": '''def graph_density_metrics(node_count: int, edges: list[tuple[int, int]]) -> tuple[float, float]:
    if node_count < 2:
        raise ValueError("need at least two nodes")
    unique_edges = {(min(u, v), max(u, v)) for u, v in edges if u != v}
    density = 2.0 * len(unique_edges) / (node_count * (node_count - 1))
    average_degree = 2.0 * len(unique_edges) / node_count
    return round(density, 4), round(average_degree, 4)

if __name__ == "__main__":
    assert graph_density_metrics(4, [(0, 1), (1, 0), (1, 2), (2, 2)]) == (0.3333, 1.0)
'''
    },

    # 3. NESTED LOOP ONLY (6 programs: P0415 - P0420)
    "P0415": {
        "domain": "Matrix & Grid Operations",
        "task": "Sum matrix entries along each diagonal offset band",
        "category": "Nested loop only",
        "code": '''def diagonal_band_sums(matrix: list[list[int]]) -> dict[int, int]:
    bands: dict[int, int] = {}
    for r, row in enumerate(matrix):
        for c, value in enumerate(row):
            offset = c - r
            bands[offset] = bands.get(offset, 0) + value
    return dict(sorted(bands.items()))

if __name__ == "__main__":
    grid = [[1, 2], [3, 4]]
    assert diagonal_band_sums(grid) == {-1: 3, 0: 5, 1: 2}
'''
    },
    "P0416": {
        "domain": "Searching and Sorting",
        "task": "Bucket sort of unit-interval floats with insertion sort inside buckets",
        "category": "Nested loop only",
        "code": '''def bucket_sort_unit(values: list[float], bucket_count: int = 5) -> list[float]:
    buckets = [[] for _ in range(bucket_count)]
    for value in values:
        index = min(int(value * bucket_count), bucket_count - 1)
        buckets[index].append(value)
    result = []
    for bucket in buckets:
        for i in range(1, len(bucket)):
            key = bucket[i]
            j = i - 1
            while j >= 0 and bucket[j] > key:
                bucket[j + 1] = bucket[j]
                j -= 1
            bucket[j + 1] = key
        result.extend(bucket)
    return result

if __name__ == "__main__":
    data = [0.42, 0.32, 0.23, 0.52, 0.25, 0.47, 0.51]
    assert bucket_sort_unit(data) == sorted(data)
'''
    },
    "P0417": {
        "domain": "Graph or Tree Traversal",
        "task": "Width of each level of a rooted tree by level-order traversal",
        "category": "Nested loop only",
        "code": '''def level_widths(children: dict[str, list[str]], root: str) -> list[int]:
    widths = []
    frontier = [root]
    while frontier:
        widths.append(len(frontier))
        next_level = []
        for node in frontier:
            for child in children.get(node, []):
                next_level.append(child)
        frontier = next_level
    return widths

if __name__ == "__main__":
    tree = {"a": ["b", "c"], "b": ["d"]}
    assert level_widths(tree, "a") == [1, 2, 1]
'''
    },
    "P0418": {
        "domain": "String Processing & Text Analysis",
        "task": "Count occurrences of a word in the rows and columns of a letter grid",
        "category": "Nested loop only",
        "code": '''def count_word_in_grid(rows: list[str], word: str) -> int:
    hits = 0
    columns = ["".join(col) for col in zip(*rows)]
    for line in rows + columns:
        for start in range(len(line) - len(word) + 1):
            if line[start:start + len(word)] == word:
                hits += 1
    return hits

if __name__ == "__main__":
    grid = ["CATX", "AXXX", "TXXX"]
    assert count_word_in_grid(grid, "CAT") == 2
'''
    },
    "P0419": {
        "domain": "Data Aggregation and Statistics",
        "task": "Running cumulative monthly sales totals per region",
        "category": "Nested loop only",
        "code": '''def cumulative_by_region(sales: dict[str, list[int]]) -> dict[str, list[int]]:
    running = {}
    for region, months in sales.items():
        total = 0
        series = []
        for amount in months:
            total += amount
            series.append(total)
        running[region] = series
    return running

if __name__ == "__main__":
    sales = {"north": [5, 3, 2], "south": [1]}
    assert cumulative_by_region(sales) == {"north": [5, 8, 10], "south": [1]}
'''
    },
    "P0420": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "One-dimensional particles bouncing between two walls over time steps",
        "category": "Nested loop only",
        "code": '''def bounce_particles(positions: list[float], velocities: list[float], width: float, steps: int) -> list[float]:
    pos = list(positions)
    vel = list(velocities)
    for _ in range(steps):
        for i in range(len(pos)):
            pos[i] += vel[i]
            if pos[i] < 0.0 or pos[i] > width:
                vel[i] = -vel[i]
                pos[i] = max(0.0, min(width, pos[i]))
    return pos

if __name__ == "__main__":
    assert bounce_particles([1.0], [2.0], 4.0, 3) == [2.0]
'''
    },

    # 4. COMPLEX CONDITIONAL ONLY (6 programs: P0421 - P0426)
    "P0421": {
        "domain": "String Processing & Text Analysis",
        "task": "Validate an ISBN-10 code including the X check character",
        "category": "Complex conditional only",
        "code": '''def is_valid_isbn10(code: str) -> bool:
    digits = code.replace("-", "")
    if len(digits) != 10 or not digits[:9].isdigit() or digits[9] not in "0123456789X":
        return False
    total = 0
    for position, char in enumerate(digits):
        value = 10 if char == "X" else int(char)
        total += (10 - position) * value
    return total % 11 == 0

if __name__ == "__main__":
    assert is_valid_isbn10("0-306-40615-2") is True
    assert is_valid_isbn10("0306406153") is False
    assert is_valid_isbn10("12345") is False
'''
    },
    "P0422": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Decide if an aircraft maintenance slot fits the overnight window",
        "category": "Complex conditional only",
        "code": '''def can_book_overnight_maintenance(start_hour: int, duration: int, crew: int, in_service: bool) -> bool:
    end_hour = (start_hour + duration) % 24
    overnight = start_hour >= 22 or start_hour < 4
    if overnight and duration <= 6 and crew >= 2 and not in_service:
        return end_hour <= 6
    return False

if __name__ == "__main__":
    assert can_book_overnight_maintenance(23, 5, 2, False) is True
    assert can_book_overnight_maintenance(23, 8, 2, False) is False
    assert can_book_overnight_maintenance(12, 2, 3, False) is False
'''
    },
    "P0423": {
        "domain": "Numerical Computation",
        "task": "Classify an integer as prime, perfect, abundant or deficient",
        "category": "Complex conditional only",
        "code": '''def classify_number(n: int) -> str:
    half = n // 2
    divisors = [d for d in range(1, half + 1) if n % d == 0]
    divisor_sum = sum(divisors)
    if n > 1 and divisor_sum == 1:
        return "prime"
    if n > 0 and divisor_sum == n and n % 2 == 0:
        return "perfect"
    return "abundant" if divisor_sum > n else "deficient"

if __name__ == "__main__":
    assert classify_number(7) == "prime"
    assert classify_number(28) == "perfect"
    assert classify_number(12) == "abundant"
    assert classify_number(8) == "deficient"
'''
    },
    "P0424": {
        "domain": "Inventory and Record Management",
        "task": "Purchase order quantity from inventory position, supplier and lifecycle status",
        "category": "Complex conditional only",
        "code": '''def needs_purchase_order(stock: dict[str, int], supplier_active: bool, discontinued: bool) -> int:
    position = stock["have"] + stock["coming"] - stock["owed"]
    if position > stock["rop"] or not supplier_active or discontinued:
        return 0
    shortfall = stock["max"] - position
    return max(0, shortfall)

if __name__ == "__main__":
    stock = dict(have=5, coming=10, owed=3, rop=20, max=50)
    assert needs_purchase_order(stock, True, False) == 38
    assert needs_purchase_order(stock, True, True) == 0
'''
    },
    "P0425": {
        "domain": "Graph or Tree Traversal",
        "task": "Check whether adding a dependency edge keeps a task graph acyclic",
        "category": "Complex conditional only",
        "code": '''def can_add_dependency(graph: dict[str, set[str]], src: str, dst: str) -> bool:
    if src == dst or src not in graph or dst not in graph:
        return False
    stack = [dst]
    seen = set()
    while stack:
        node = stack.pop()
        if node == src:
            return False
        seen.add(node)
        stack.extend(n for n in graph[node] if n not in seen)
    return True

if __name__ == "__main__":
    deps = {"a": {"b"}, "b": {"c"}, "c": set()}
    assert can_add_dependency(deps, "c", "a") is False
    assert can_add_dependency(deps, "a", "c") is True
'''
    },
    "P0426": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Vending machine decision from credit, stock, change float and lock state",
        "category": "Complex conditional only",
        "code": '''def vend_item(credit: int, price: int, stock: int, change_coins: int, selection_locked: bool) -> tuple[str, int]:
    change_due = credit - price
    if credit >= price and stock > 0 and not selection_locked:
        if change_due <= change_coins:
            return "dispense", change_due
        return "exact change only", credit
    return "insufficient", credit

if __name__ == "__main__":
    assert vend_item(150, 120, 3, 50, False) == ("dispense", 30)
    assert vend_item(150, 120, 3, 10, False) == ("exact change only", 150)
    assert vend_item(100, 120, 3, 50, False) == ("insufficient", 100)
'''
    },

    # 5. LONG STATEMENT AND NESTED LOOP (6 programs: P0427 - P0432)
    "P0427": {
        "domain": "Matrix & Grid Operations",
        "task": "Normalised two-dimensional Gaussian convolution kernel",
        "category": "Long statement and nested loop",
        "code": '''import math

def gaussian_kernel_2d(size: int, sigma: float) -> list[list[float]]:
    half = size // 2
    kernel = []
    for y in range(-half, half + 1):
        row = []
        for x in range(-half, half + 1):
            row.append(math.exp(-(x * x + y * y) / (2.0 * sigma * sigma)) / (2.0 * math.pi * sigma * sigma))
        kernel.append(row)
    total = sum(sum(row) for row in kernel)
    return [[round(v / total, 4) for v in row] for row in kernel]

if __name__ == "__main__":
    k = gaussian_kernel_2d(3, 1.0)
    assert k[1][1] == max(map(max, k))
    assert abs(sum(map(sum, k)) - 1.0) < 1e-3
'''
    },
    "P0428": {
        "domain": "Data Aggregation and Statistics",
        "task": "Autocorrelation at each lag with Bartlett confidence band",
        "category": "Long statement and nested loop",
        "code": '''import math

def autocorrelation_profile(series: list[float], max_lag: int) -> list[tuple[float, float]]:
    n = len(series)
    mean = sum(series) / n
    variance = sum((x - mean) ** 2 for x in series)
    profile = []
    for lag in range(1, max_lag + 1):
        covariance = 0.0
        for t in range(n - lag):
            covariance += (series[t] - mean) * (series[t + lag] - mean)
        r = covariance / variance
        earlier = [rho for rho, _ in profile]
        bartlett_band = 1.96 * math.sqrt((1.0 + 2.0 * sum(rho * rho for rho in earlier)) / n)
        profile.append((round(r, 4), round(bartlett_band, 4)))
    return profile

if __name__ == "__main__":
    profile = autocorrelation_profile([1.0, 2.0, 3.0, 4.0, 5.0, 6.0], 2)
    assert profile[0] == (0.5, 0.8002)
'''
    },
    "P0429": {
        "domain": "Inventory and Record Management",
        "task": "Value stock held across warehouses using unit costs and site exchange rates",
        "category": "Long statement and nested loop",
        "code": '''def warehouse_stock_valuation(warehouses: dict[str, dict[str, int]], unit_costs: dict[str, float], fx_rates: dict[str, float]) -> dict[str, float]:
    valuation = {}
    for site, bins in warehouses.items():
        site_total = 0.0
        for sku, quantity in bins.items():
            site_total += quantity * unit_costs.get(sku, 0.0) * fx_rates.get(site, 1.0)
        valuation[site] = round(site_total, 2)
    return valuation

if __name__ == "__main__":
    sites = {"DE": {"A": 10}, "US": {"A": 2, "B": 1}}
    costs = {"A": 5.0, "B": 20.0}
    assert warehouse_stock_valuation(sites, costs, {"DE": 1.1}) == {"DE": 55.0, "US": 30.0}
'''
    },
    "P0430": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Daily crew load profile and utilisation relative to the peak day",
        "category": "Long statement and nested loop",
        "code": '''def resource_load_profile(tasks: list[tuple[str, int, int, int]], horizon: int) -> tuple[list[int], list[float]]:
    load = [0] * horizon
    for _, start, duration, crew in tasks:
        for day in range(start, min(start + duration, horizon)):
            load[day] += crew
    peak = max(load) if load else 0
    utilisation = [round(day_load / peak, 2) if peak else 0.0 for day_load in load]
    return load, utilisation

if __name__ == "__main__":
    tasks = [("dig", 0, 2, 3), ("pour", 1, 2, 2)]
    assert resource_load_profile(tasks, 4) == ([3, 5, 2, 0], [0.6, 1.0, 0.4, 0.0])
'''
    },
    "P0431": {
        "domain": "String Processing & Text Analysis",
        "task": "Edit distance with cheaper substitutions between adjacent keyboard keys",
        "category": "Long statement and nested loop",
        "code": '''KEYBOARD_ROWS = ("qwertyuiop", "asdfghjkl", "zxcvbnm")

def keyboard_edit_distance(source: str, target: str) -> float:
    position = {ch: (r, row.index(ch)) for r, row in enumerate(KEYBOARD_ROWS) for ch in row}
    rows, cols = len(source) + 1, len(target) + 1
    table = [[float(i + j) if i == 0 or j == 0 else 0.0 for j in range(cols)] for i in range(rows)]
    for i in range(1, rows):
        for j in range(1, cols):
            a, b = source[i - 1], target[j - 1]
            pa, pb = position.get(a, (9, 9)), position.get(b, (-9, -9))
            near = abs(pa[0] - pb[0]) + abs(pa[1] - pb[1]) == 1
            cost = 0.0 if a == b else (0.5 if near else 1.0)
            table[i][j] = min(table[i - 1][j] + 1.0, table[i][j - 1] + 1.0, table[i - 1][j - 1] + cost)
    return table[-1][-1]

if __name__ == "__main__":
    assert keyboard_edit_distance("cat", "cst") == 0.5
    assert keyboard_edit_distance("cat", "cat") == 0.0
    assert keyboard_edit_distance("", "ab") == 2.0
'''
    },
    "P0432": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Ant colony pheromone evaporation and tour-length weighted deposit",
        "category": "Long statement and nested loop",
        "code": '''def evaporate_and_deposit(pheromone: list[list[float]], tours: list[list[int]], tour_lengths: list[float], rho: float) -> list[list[float]]:
    size = len(pheromone)
    updated = [[(1.0 - rho) * pheromone[i][j] for j in range(size)] for i in range(size)]
    for tour, length in zip(tours, tour_lengths):
        for a, b in zip(tour, tour[1:] + tour[:1]):
            updated[a][b] += 1.0 / length
            updated[b][a] += 1.0 / length
    return [[round(value, 4) for value in row] for row in updated]

if __name__ == "__main__":
    trail = [[0.0, 1.0], [1.0, 0.0]]
    assert evaporate_and_deposit(trail, [[0, 1]], [2.0], 0.5) == [[0.0, 1.5], [1.5, 0.0]]
'''
    },

    # 6. LONG STATEMENT AND COMPLEX CONDITIONAL (6 programs: P0433 - P0438)
    "P0433": {
        "domain": "Numerical Computation",
        "task": "Wind turbine power output with cut-in, rated and cut-out speeds",
        "category": "Long statement and complex conditional",
        "code": '''def turbine_power_kw(wind_speed: float, rotor_diameter_m: float, air_density: float = 1.225) -> float:
    cut_in, rated_speed, cut_out = 3.0, 12.0, 25.0
    if wind_speed < cut_in or wind_speed >= cut_out or rotor_diameter_m <= 0:
        return 0.0
    swept_area = 3.141592653589793 * (rotor_diameter_m / 2.0) ** 2
    effective_speed = min(wind_speed, rated_speed)
    power_kw = 0.5 * air_density * swept_area * effective_speed ** 3 * 0.42 / 1000.0
    return round(power_kw, 1)

if __name__ == "__main__":
    assert turbine_power_kw(2.0, 100.0) == 0.0
    assert turbine_power_kw(30.0, 100.0) == 0.0
    assert turbine_power_kw(12.0, 100.0) == turbine_power_kw(15.0, 100.0) > 0
'''
    },
    "P0434": {
        "domain": "Data Aggregation and Statistics",
        "task": "Two-proportion z-test verdict for an A/B conversion experiment",
        "category": "Long statement and complex conditional",
        "code": '''import math

def ab_test_verdict(conversions_a: int, visitors_a: int, conversions_b: int, visitors_b: int) -> str:
    rate_a, rate_b = conversions_a / visitors_a, conversions_b / visitors_b
    pooled = (conversions_a + conversions_b) / (visitors_a + visitors_b)
    standard_error = math.sqrt(pooled * (1 - pooled) * (1 / visitors_a + 1 / visitors_b))
    z_score = (rate_b - rate_a) / standard_error if standard_error > 0 else 0.0
    if z_score > 1.96 and visitors_a >= 100 and visitors_b >= 100:
        return "B wins"
    if z_score < -1.96 and visitors_a >= 100 and visitors_b >= 100:
        return "A wins"
    return "inconclusive"

if __name__ == "__main__":
    assert ab_test_verdict(100, 1000, 150, 1000) == "B wins"
    assert ab_test_verdict(10, 50, 20, 50) == "inconclusive"
'''
    },
    "P0435": {
        "domain": "String Processing & Text Analysis",
        "task": "Parse a compact duration string such as 1h30m15s into seconds",
        "category": "Long statement and complex conditional",
        "code": '''import re

def parse_duration_seconds(text: str) -> int:
    match = re.fullmatch("(?:([0-9]+)h)?(?:([0-9]+)m)?(?:([0-9]+)s)?", text.strip())
    if match is None or not text.strip():
        raise ValueError("bad duration")
    hours, minutes, seconds = (int(part) if part else 0 for part in match.groups())
    if minutes >= 60 or seconds >= 60 or hours > 999:
        raise ValueError("component out of range")
    return hours * 3600 + minutes * 60 + seconds

if __name__ == "__main__":
    assert parse_duration_seconds("1h30m15s") == 5415
    assert parse_duration_seconds("45s") == 45
'''
    },
    "P0436": {
        "domain": "Inventory and Record Management",
        "task": "Release or quarantine a pharmaceutical lot by potency drift and expiry",
        "category": "Long statement and complex conditional",
        "code": '''def lot_release_decision(lot: dict[str, float], days_to_expiry: int, coa_received: bool) -> tuple[str, float]:
    potency_drift = abs(lot["assay"] - lot["label"]) / lot["label"] * 100.0
    sellable_fraction = max(0.0, min(1.0, days_to_expiry / 365.0)) * (1.0 - lot["damaged"])
    if potency_drift <= 5.0 and coa_received and days_to_expiry > 30:
        return "release", round(sellable_fraction, 3)
    return "quarantine", 0.0

if __name__ == "__main__":
    lot = dict(assay=98.0, label=100.0, damaged=0.1)
    assert lot_release_decision(lot, 365, True) == ("release", 0.9)
    assert lot_release_decision(lot, 10, True) == ("quarantine", 0.0)
'''
    },
    "P0437": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Autoscale service replicas from CPU load and request queue depth",
        "category": "Long statement and complex conditional",
        "code": '''def autoscale_replicas(cpu_pct: float, queue_depth: int, replicas: int, min_r: int = 2, max_r: int = 20) -> int:
    pressure = max(cpu_pct / 70.0, queue_depth / max(1, replicas * 50))
    desired = max(min_r, min(max_r, int(replicas * pressure + 0.999)))
    if cpu_pct < 30.0 and queue_depth == 0 and replicas > min_r:
        return max(min_r, replicas - 1)
    return desired

if __name__ == "__main__":
    assert autoscale_replicas(35.0, 0, 4) == 2
    assert autoscale_replicas(20.0, 0, 4) == 3
    assert autoscale_replicas(140.0, 0, 4) == 8
'''
    },
    "P0438": {
        "domain": "Graph or Tree Traversal",
        "task": "Cost of a route through a weighted road graph avoiding closed junctions",
        "category": "Long statement and complex conditional",
        "code": '''def evaluate_route(path: list[str], weights: dict[tuple[str, str], float], closed: set[str], budget: float) -> float:
    legs = list(zip(path, path[1:]))
    total_cost = sum(weights.get(leg, weights.get((leg[1], leg[0]), float("inf"))) for leg in legs)
    if len(path) < 2 or total_cost > budget or closed.intersection(path):
        return -1.0
    return round(total_cost, 2)

if __name__ == "__main__":
    roads = {("a", "b"): 2.0, ("c", "b"): 3.5}
    assert evaluate_route(["a", "b", "c"], roads, set(), 10.0) == 5.5
    assert evaluate_route(["a", "b", "c"], roads, {"b"}, 10.0) == -1.0
'''
    },

    # 7. NESTED LOOP AND COMPLEX CONDITIONAL (6 programs: P0439 - P0444)
    "P0439": {
        "domain": "Matrix & Grid Operations",
        "task": "Count 3x3 magic squares made of the digits 1-9 inside a grid",
        "category": "Nested loop and complex conditional",
        "code": '''def count_magic_squares(grid: list[list[int]]) -> int:
    found = 0
    for r in range(len(grid) - 2):
        for c in range(len(grid[0]) - 2):
            block = [row[c:c + 3] for row in grid[r:r + 3]]
            values = sorted(v for row in block for v in row)
            rows_ok = all(sum(row) == 15 for row in block)
            cols_ok = all(sum(col) == 15 for col in zip(*block))
            diag = block[0][0] + block[1][1] + block[2][2]
            if values == list(range(1, 10)) and rows_ok and cols_ok and diag == 15:
                found += 1
    return found

if __name__ == "__main__":
    grid = [[4, 3, 8, 4], [9, 5, 1, 9], [2, 7, 6, 2]]
    assert count_magic_squares(grid) == 1
'''
    },
    "P0440": {
        "domain": "Data Aggregation and Statistics",
        "task": "Detect sensors reporting stuck non-zero values over consecutive readings",
        "category": "Nested loop and complex conditional",
        "code": '''def stuck_sensor_runs(readings: dict[str, list[float]], min_run: int, tolerance: float) -> dict[str, int]:
    stuck = {}
    for sensor, values in readings.items():
        run = 1
        longest = 1
        for prev, curr in zip(values, values[1:]):
            if abs(curr - prev) <= tolerance and curr != 0.0 and prev != 0.0:
                run += 1
            else:
                run = 1
            longest = max(longest, run)
        if longest >= min_run:
            stuck[sensor] = longest
    return stuck

if __name__ == "__main__":
    data = {"t1": [1.0, 1.0, 1.0, 2.0], "t2": [1.0, 2.0, 3.0]}
    assert stuck_sensor_runs(data, 3, 0.01) == {"t1": 3}
'''
    },
    "P0441": {
        "domain": "Graph or Tree Traversal",
        "task": "Count grid cells reachable from a start within a fuel budget",
        "category": "Nested loop and complex conditional",
        "code": '''from collections import deque

def cells_within_fuel(grid: list[str], start: tuple[int, int], fuel: int) -> int:
    rows, cols = len(grid), len(grid[0])
    seen = {start}
    queue = deque([(start, 0)])
    while queue:
        (r, c), used = queue.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            inside = 0 <= nr < rows and 0 <= nc < cols
            if inside and grid[nr][nc] != "#" and (nr, nc) not in seen and used < fuel:
                seen.add((nr, nc))
                queue.append(((nr, nc), used + 1))
    return len(seen)

if __name__ == "__main__":
    assert cells_within_fuel(["..#", "...", "#.."], (0, 0), 2) == 4
'''
    },
    "P0442": {
        "domain": "String Processing & Text Analysis",
        "task": "Find pairs of distinct words that are cyclic rotations of each other",
        "category": "Nested loop and complex conditional",
        "code": '''def rotation_pairs(words: list[str]) -> list[tuple[str, str]]:
    pairs = []
    for i, first in enumerate(words):
        for second in words[i + 1:]:
            same_size = len(first) == len(second)
            if same_size and first != second and second in first + first:
                pairs.append((first, second))
    return pairs

if __name__ == "__main__":
    result = rotation_pairs(["abcd", "cdab", "xyz", "abcd"])
    assert result == [("abcd", "cdab"), ("cdab", "abcd")]
'''
    },
    "P0443": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Allocate parking bays by vehicle size and charger requirement",
        "category": "Nested loop and complex conditional",
        "code": '''def allocate_parking(vehicles: list[tuple[str, str, bool]], bays: list[tuple[str, str, bool]]) -> tuple[dict[str, str], list[str]]:
    free = {bay[0]: (bay[1], bay[2]) for bay in bays}
    allocation = {}
    waiting = []
    for plate, size, needs_charger in vehicles:
        best_id, best_waste = None, 99
        for bay_id, (bay_size, has_charger) in free.items():
            fits = bay_size == size or bay_size == "large"
            spare_charger = has_charger and not needs_charger
            waste = int(bay_size != size) + int(spare_charger)
            if fits and (has_charger or not needs_charger) and waste < best_waste:
                best_id, best_waste = bay_id, waste
        if best_id is None:
            waiting.append(plate)
        else:
            allocation[plate] = best_id
            del free[best_id]
    return allocation, waiting

if __name__ == "__main__":
    cars = [("CAR2", "small", False), ("EV1", "small", True)]
    cars.append(("VAN", "large", False))
    bays = [("B2", "large", True), ("B1", "small", False)]
    assert allocate_parking(cars, bays) == ({"CAR2": "B1", "EV1": "B2"}, ["VAN"])
'''
    },
    "P0444": {
        "domain": "Small Simulation and Rule-based Systems",
        "task": "Deterministic cellular automaton traffic flow on a circular road",
        "category": "Nested loop and complex conditional",
        "code": '''def traffic_ca_steps(road: list[int], vmax: int, steps: int) -> list[int]:
    length = len(road)
    for _ in range(steps):
        new_road = [-1] * length
        for i, speed in enumerate(road):
            if speed < 0:
                continue
            gap = 0
            while gap < vmax and gap < length - 1 and road[(i + gap + 1) % length] < 0:
                gap += 1
            new_speed = min(speed + 1, vmax, gap)
            new_road[(i + new_speed) % length] = new_speed
        road = new_road
    return road

if __name__ == "__main__":
    assert traffic_ca_steps([0, -1, -1, -1, -1], 2, 1) == [-1, 1, -1, -1, -1]
    assert traffic_ca_steps([0, -1, -1, -1, -1], 2, 2) == [-1, -1, -1, 2, -1]
'''
    },

    # 8. ALL THREE TARGET ISSUES (6 programs: P0445 - P0450)
    "P0445": {
        "domain": "Matrix & Grid Operations",
        "task": "Flag undrained local-minimum cells with heavy rainfall as flood prone",
        "category": "All three target issues",
        "code": '''def flood_prone_cells(elevation: list[list[float]], rainfall: list[list[float]], drains: set[tuple[int, int]]) -> list[tuple[int, int]]:
    rows, cols = len(elevation), len(elevation[0])
    prone = []
    for r in range(rows):
        for c in range(cols):
            lower_neighbours = sum(1 for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)) if 0 <= r + dr < rows and 0 <= c + dc < cols and elevation[r + dr][c + dc] < elevation[r][c])
            if lower_neighbours == 0 and rainfall[r][c] > 50.0 and (r, c) not in drains:
                prone.append((r, c))
    return prone

if __name__ == "__main__":
    heights = [[1.0, 2.0], [2.0, 3.0]]
    rain = [[60.0, 60.0], [60.0, 60.0]]
    assert flood_prone_cells(heights, rain, set()) == [(0, 0)]
    assert flood_prone_cells(heights, rain, {(0, 0)}) == []
'''
    },
    "P0446": {
        "domain": "Data Aggregation and Statistics",
        "task": "Western Electric control chart rule violations per process stream",
        "category": "All three target issues",
        "code": '''def western_electric_alerts(processes: dict[str, list[float]], mean: float, sigma: float) -> dict[str, list[int]]:
    alerts = {}
    for name, samples in processes.items():
        hits = []
        for i, value in enumerate(samples):
            beyond_three = abs(value - mean) > 3.0 * sigma
            recent = samples[max(0, i - 2):i + 1]
            two_sigma_pair = sum(1 for x in recent if abs(x - mean) > 2.0 * sigma) >= 2
            if beyond_three or (two_sigma_pair and len(recent) == 3):
                hits.append(i)
        if hits:
            alerts[name] = hits
    return alerts

if __name__ == "__main__":
    stream = {"p": [0.0, 2.5, 2.5, 0.0, 4.0]}
    assert western_electric_alerts(stream, 0.0, 1.0) == {"p": [2, 3, 4]}
'''
    },
    "P0447": {
        "domain": "Inventory and Record Management",
        "task": "Flag costly cycle-count variances against system stock by location",
        "category": "All three target issues",
        "code": '''def cycle_count_variances(counts: dict[str, dict[str, int]], system: dict[str, dict[str, int]], unit_cost: dict[str, float]) -> list[tuple[str, str, float]]:
    flagged = []
    for location, skus in counts.items():
        for sku, counted in skus.items():
            expected = system.get(location, {}).get(sku, 0)
            variance_value = abs(counted - expected) * unit_cost.get(sku, 0.0) * (1.25 if location.startswith("CAGE") else 1.0)
            if variance_value > 100.0 and expected > 0 and counted != expected:
                flagged.append((location, sku, round(variance_value, 2)))
    return flagged

if __name__ == "__main__":
    counted = {"A1": {"x": 8}, "CAGE1": {"y": 1}}
    booked = {"A1": {"x": 10}, "CAGE1": {"y": 2}}
    prices = {"x": 60.0, "y": 100.0}
    assert cycle_count_variances(counted, booked, prices) == [("A1", "x", 120.0), ("CAGE1", "y", 125.0)]
'''
    },
    "P0448": {
        "domain": "Scheduling and Resource Allocation",
        "task": "Schedule EV charging into the cheapest hours under charger capacity",
        "category": "All three target issues",
        "code": '''def schedule_ev_charging(vehicles: list[tuple[str, int, float, int]], chargers: int, price_by_hour: list[float]) -> dict[str, list[int]]:
    plan = {}
    usage = [0] * len(price_by_hour)
    for plate, arrive, needed_kwh, depart in sorted(vehicles, key=lambda v: v[3]):
        hours_needed = int(needed_kwh / 7.2 + 0.999)
        cheapest_hours = sorted(range(arrive, depart), key=lambda h: (price_by_hour[h], h))
        chosen = []
        for hour in cheapest_hours:
            if usage[hour] < chargers and len(chosen) < hours_needed and price_by_hour[hour] < 0.5:
                usage[hour] += 1
                chosen.append(hour)
        plan[plate] = sorted(chosen)
    return plan

if __name__ == "__main__":
    evs = [("EV1", 0, 14.0, 4), ("EV2", 0, 7.0, 4)]
    assert schedule_ev_charging(evs, 1, [0.3, 0.1, 0.2, 0.4]) == {"EV1": [1, 2], "EV2": [0]}
'''
    },
    "P0449": {
        "domain": "String Processing & Text Analysis",
        "task": "Report document pairs with high word-shingle Jaccard overlap",
        "category": "All three target issues",
        "code": '''def shingle_overlap_report(documents: dict[str, str], k: int, threshold: float) -> list[tuple[str, str, float]]:
    names = sorted(documents)
    shingles = {}
    for name in names:
        words = documents[name].lower().split()
        shingles[name] = {tuple(words[i:i + k]) for i in range(len(words) - k + 1)}
    report = []
    for i, first in enumerate(names):
        for second in names[i + 1:]:
            a, b = shingles[first], shingles[second]
            jaccard = len(a & b) / len(a | b) if a | b else 0.0
            if jaccard >= threshold and len(a) >= 2 and len(b) >= 2:
                report.append((first, second, round(jaccard, 3)))
    return report

if __name__ == "__main__":
    docs = {
        "a": "the quick brown fox jumps",
        "b": "the quick brown fox sleeps",
        "c": "nothing alike here at all",
    }
    assert shingle_overlap_report(docs, 2, 0.4) == [("a", "b", 0.6)]
'''
    },
    "P0450": {
        "domain": "Graph or Tree Traversal",
        "task": "Critical path and project duration of a task precedence network",
        "category": "All three target issues",
        "code": '''def critical_path_tasks(durations: dict[str, int], predecessors: dict[str, list[str]], order: list[str]) -> tuple[int, list[str]]:
    earliest_finish = {}
    for task in order:
        start = 0
        for pred in predecessors.get(task, []):
            start = max(start, earliest_finish[pred])
        earliest_finish[task] = start + durations[task]
    project_end = max(earliest_finish.values())
    latest_finish = {task: project_end for task in order}
    for task in reversed(order):
        for pred in predecessors.get(task, []):
            latest_finish[pred] = min(latest_finish[pred], latest_finish[task] - durations[task])
    critical = []
    for task in order:
        slack = latest_finish[task] - earliest_finish[task]
        if slack == 0 and durations[task] > 0 and task in latest_finish:
            critical.append(task)
    return project_end, critical

if __name__ == "__main__":
    durations = {"A": 3, "B": 2, "C": 4, "D": 1}
    preds = {"C": ["A"], "D": ["B", "C"]}
    assert critical_path_tasks(durations, preds, ["A", "B", "C", "D"]) == (8, ["A", "C", "D"])
'''
    },
}

BATCHES = [
    {
        "batch_id": "Batch 9",
        "model_id": "claude-opus-5.5",
        "prompt_version": "v9.0-expansion",
        "programs": BATCH9_PROGRAMS,
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