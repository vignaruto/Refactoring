def trial_division_primes(low, high):
    found = []
    for n in range(max(2, low), high + 1):
        d = 2
        while d * d <= n and n % d:
            d += 1
        if d * d > n:
            found.append(n)
    return found

if __name__ == "__main__":
    assert trial_division_primes(10, 30) == [11, 13, 17, 19, 23, 29]
    assert trial_division_primes(0, 3) == [2, 3]
