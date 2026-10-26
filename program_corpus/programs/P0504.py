def classify_log_severity(line: str) -> str:
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
