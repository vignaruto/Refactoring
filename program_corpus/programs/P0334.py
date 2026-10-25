import math

def welch_t_decision(mean1: float, var1: float, n1: int, mean2: float, var2: float, n2: int, critical_t: float) -> tuple[float, bool]:
    if n1 < 2 or n2 < 2 or var1 < 0.0 or var2 < 0.0 or (var1 == 0.0 and var2 == 0.0):
        raise ValueError("invalid sample statistics")
    se = math.sqrt(var1 / n1 + var2 / n2)
    t_stat = (mean1 - mean2) / se
    df_num = (var1 / n1 + var2 / n2) ** 2
    df_den = (var1 / n1) ** 2 / (n1 - 1) + (var2 / n2) ** 2 / (n2 - 1)
    reject = abs(t_stat) >= critical_t and (df_num / df_den) >= 4.0 and se > 0.0
    return round(t_stat, 4), reject

if __name__ == "__main__":
    assert welch_t_decision(10.0, 4.0, 16, 7.0, 4.0, 16, 2.0) == (4.2426, True)
