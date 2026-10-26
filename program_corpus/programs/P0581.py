def tag_cooccurrence(posts, minimum):
    pairs = {}
    for tags in posts:
        unique = sorted(set(tags))
        for i in range(len(unique)):
            for j in range(i + 1, len(unique)):
                key = (unique[i], unique[j])
                pairs[key] = pairs.get(key, 0) + 1
    strong = {}
    for key, count in pairs.items():
        if count >= minimum and key[0] != key[1] and "misc" not in key:
            strong[key] = count
    return strong

if __name__ == "__main__":
    posts = [["py", "ml"], ["ml", "py", "misc"], ["py", "web"]]
    assert tag_cooccurrence(posts, 2) == {("ml", "py"): 2}
