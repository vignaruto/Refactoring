def count_palindromic_substrings(tokens: list[str]) -> int:
    total_palindromes = 0
    for word in tokens:
        n = len(word)
        for i in range(n):
            for j in range(i + 1, n + 1):
                sub = word[i:j]
                if len(sub) > 1:
                    if sub == sub[::-1]:
                        total_palindromes += 1
    return total_palindromes

if __name__ == "__main__":
    assert count_palindromic_substrings(["racecar", "noon"]) == 5
