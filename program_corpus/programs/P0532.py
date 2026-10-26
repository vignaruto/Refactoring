def snake_to_title(name: str, keep_upper: set[str]) -> str:
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
