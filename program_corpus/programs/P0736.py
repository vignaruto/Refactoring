def dedupe_contacts(contacts):
    seen_emails, seen_phones = set(), set()
    kept = []
    for c in contacts:
        email = c.get("email", "").strip().lower()
        raw = c.get("phone", "")
        phone = "".join(ch for ch in raw if ch.isdigit())
        if email in seen_emails and email or phone in seen_phones and phone:
            continue
        seen_emails.add(email)
        seen_phones.add(phone)
        kept.append(c)
    return kept, len(contacts) - len(kept), round(len(kept) / max(len(contacts), 1), 2)

if __name__ == "__main__":
    contacts = [{"email": "A@x.com", "phone": "12-3"}]
    contacts.append({"email": "a@x.com"})
    contacts.append({"phone": "123"})
    contacts.append({"email": "b@x.com", "phone": "999"})
    kept, removed, share = dedupe_contacts(contacts)
    assert [c.get("phone") for c in kept] == ["12-3", "999"]
    assert (removed, share) == (2, 0.5)
