def month_end_balance(balance, apr, fee, deposits, withdrawals):
    interest = balance * apr / 12 if balance > 0 else balance * (apr + 0.05) / 12
    closing = balance + interest + sum(deposits) - sum(withdrawals) - fee * (balance < 500)
    return round(closing, 2)

if __name__ == "__main__":
    assert month_end_balance(1000, 0.12, 5, [100], [50]) == 1060.0
    assert month_end_balance(-100, 0.12, 5, [], []) == -106.42
