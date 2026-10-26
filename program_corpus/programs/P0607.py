def select_settings(config, prefix, low, high):
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
