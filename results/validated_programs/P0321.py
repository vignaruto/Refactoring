def is_valid_semver(version: str) -> bool:
    core, sep, prerelease = version.partition("-")
    parts = core.split(".")
    condition = len(parts) != 3
    if not condition:
        condition = sep == '-' and not prerelease
    if condition:
        return False
    for num in parts:
        condition_2 = not num.isdigit()
        if not condition_2:
            condition_2 = len(num) > 1 and num.startswith('0')
        if condition_2:
            return False
    if prerelease:
        for ident in prerelease.split("."):
            if not ident or not ident.replace("-", "").isalnum():
                return False
            condition_3 = ident.isdigit() and len(ident) > 1
            if condition_3:
                condition_3 = ident.startswith('0')
            if condition_3:
                return False
    return True

if __name__ == "__main__":
    assert is_valid_semver("1.2.3-alpha.1") is True
    assert is_valid_semver("01.2.3") is False
    assert is_valid_semver("1.2.3-01") is False
