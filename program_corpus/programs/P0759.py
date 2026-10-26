def format_address(name, street, city, postcode, country="", attention=""):
    lines = [name.strip().title()]
    if attention:
        lines.append("Attn: " + attention.strip())
    lines.append(street.strip())
    lines.append(f"{city.strip().upper()} {postcode.strip().upper()}".strip())
    if country:
        lines.append(country.strip().upper())
    return [line for line in lines if line]

if __name__ == "__main__":
    name, street = " jane doe", "1 High St"
    city, code = "leeds", "ls1 4ap"
    lines = format_address(name, street, city, code, "uk")
    assert lines == ["Jane Doe", "1 High St", "LEEDS LS1 4AP", "UK"]
