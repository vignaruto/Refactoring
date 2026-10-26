def duplicate_contacts(contacts: list[dict[str, str]]) -> list[tuple[int, int]]:
    pairs = []
    for i in range(len(contacts)):
        for j in range(i + 1, len(contacts)):
            a, b = contacts[i], contacts[j]
            same_email = a["email"].lower() == b["email"].lower()
            same_phone = a["phone"][-7:] == b["phone"][-7:]
            if same_email or (same_phone and a["name"][0] == b["name"][0]):
                pairs.append((i, j))
    return pairs

if __name__ == "__main__":
    c1 = dict(name="Ann", email="A@x.com", phone="5551234567")
    c2 = dict(name="Al", email="al@y.com", phone="15551234567")
    c3 = dict(name="Bob", email="a@X.com", phone="000")
    assert duplicate_contacts([c1, c2, c3]) == [(0, 1), (0, 2)]
