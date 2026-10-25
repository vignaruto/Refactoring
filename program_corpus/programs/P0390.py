def suggest_friends(friends: dict[str, set[str]], interests: dict[str, set[str]]) -> list[tuple[str, str]]:
    suggestions = []
    for user, circle in friends.items():
        for friend in circle:
            for candidate in friends.get(friend, set()):
                shared = interests[user] & interests[candidate]
                if candidate != user and candidate not in circle and len(shared) >= 2:
                    suggestions.append((user, candidate))
    return sorted(set(suggestions))

if __name__ == "__main__":
    f = {"a": {"b"}, "b": {"a", "c"}, "c": {"b"}}
    tags = {"a": {"x", "y"}, "b": set(), "c": {"x", "y", "z"}}
    assert suggest_friends(f, tags) == [("a", "c"), ("c", "a")]
