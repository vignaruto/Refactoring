def is_safe_external_uri(
    uri: str, allow_custom_ports: bool, allow_https_only: bool
) -> bool:
    lower_uri = uri.lower()
    is_http = lower_uri.startswith("http://")
    is_https = lower_uri.startswith("https://")
    is_loopback = "localhost" in lower_uri or "127.0.0.1" in lower_uri
    is_internal = "192.168." in lower_uri or "10." in lower_uri
    if ((is_https or (is_http and not allow_https_only)) and not is_loopback) and not is_internal:
        return True
    return False

if __name__ == "__main__":
    assert is_safe_external_uri("https://api.external-service.org/v1", False, True) is True
