import itertools

def longest_common_substring(str1: str, str2: str) -> str:
    m = len(str1)
    n = len(str2)
    max_len = 0
    end_idx = 0
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i, j in itertools.product(range(1, m + 1), range(1, n + 1)):
        if str1[i - 1] == str2[j - 1]:
            dp[i][j] = dp[i - 1][j - 1] + 1
            if dp[i][j] > max_len:
                max_len = dp[i][j]
                end_idx = i
        else:
            dp[i][j] = 0
    return str1[end_idx - max_len:end_idx]

if __name__ == "__main__":
    assert longest_common_substring("photograph", "tomography") == "ograph"
