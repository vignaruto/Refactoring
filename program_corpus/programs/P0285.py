def http_freshness_seconds(status: int, headers: dict[str, str], shared_cache: bool, response_age_s: int) -> int:
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
