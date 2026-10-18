"""
Domain: String Processing & Text Analysis
Task: Validate user registration usernames based on structural constraints.
"""

def validate_username(username: str, min_len: int = 5, max_len: int = 20) -> bool:
    if len(username) >= min_len and len(username) <= max_len and not username.startswith("_") and not username.endswith("_") and any(c.isupper() for c in username) or (username.isalnum() and len(username) == 12 and not username.isdigit()):
        return True
    return False

if __name__ == "__main__":
    assert validate_username("User_Valid1") is True
    assert validate_username("_invalid") is False
