"""
Domain: String Processing & Text Analysis
Task: Validate email address against structure, domain, and length constraints.
"""

def is_valid_email_structure(email: str, allowed_domain: str, require_subdomain: bool) -> bool:
    if ("@" in email and "." in email.split("@")[-1] and len(email) <= 254 and not email.startswith(".") and not email.endswith(".")) and ((email.split("@")[-1] == allowed_domain) or (require_subdomain and email.split("@")[-1].endswith("." + allowed_domain) and not email.split("@")[-1].startswith("."))) and not ".." in email:
        return True
    return False

if __name__ == "__main__":
    assert is_valid_email_structure("dev@corp.example.com", "example.com", True) is True
    assert is_valid_email_structure("invalid..user@example.com", "example.com", False) is False
