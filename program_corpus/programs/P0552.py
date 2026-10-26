def digits_only(text):
    return "".join(ch for ch in text if ch.isdigit())

def same_contact(a, b):
    mail_a = a.get("email", "").lower()
    mail_b = b.get("email", "").lower()
    if mail_a and mail_a == mail_b:
        return True
    phone_a = digits_only(a.get("phone", ""))
    phone_b = digits_only(b.get("phone", ""))
    if phone_a and phone_a == phone_b and a["last"].lower() == b["last"].lower():
        return True
    return False

if __name__ == "__main__":
    x = {"email": "Ann@x.com", "last": "Lee"}
    y = {"email": "ann@X.com", "last": "Li"}
    assert same_contact(x, y)
    p = {"phone": "(555) 010-2000", "last": "Rao"}
    q = {"phone": "555 010 2000", "last": "rao"}
    assert same_contact(p, q)
    assert not same_contact(p, {"phone": "5550102000", "last": "Roy"})
