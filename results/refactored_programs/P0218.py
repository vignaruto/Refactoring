import itertools

def scs_length(str1: str, str2: str) -> int:
    m = len(str1)
    n = len(str2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i, j in itertools.product(range(m + 1), range(n + 1)):
        if i == 0:
            dp[i][j] = j
        elif j == 0:
            dp[i][j] = i
        elif str1[i - 1] == str2[j - 1]:
            dp[i][j] = 1 + dp[i - 1][j - 1]
        else:
            dp[i][j] = 1 + min(dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]

if __name__ == "__main__":
    assert scs_length("geek", "eke") == 5
