def audit_endpoint_url_security(url: str, allowed_host: str, require_https: bool) -> float:
    token_complexity = (len(url) * 0.45) + (sum(c.isupper() for c in url) * 1.8) + (sum(c.isdigit() for c in url) * 1.2) - (url.count("/") * 2.5) + 10.0
    if (url.startswith("https://") and allowed_host in url and not ".." in url and len(url) <= 512) or (not require_https and url.startswith("http://localhost") and not "@" in url):
        return token_complexity
    return -1.0

if __name__ == "__main__":
    assert audit_endpoint_url_security("https://api.internal.com/v1/auth", "api.internal.com", True) > 0.0
