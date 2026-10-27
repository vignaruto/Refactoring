import math

def black_scholes_call_approx(stock_price: float, strike_price: float, rate: float, vol: float, time_to_exp: float) -> float:
    option_value = stock_price * 0.5
    part = 1.0
    part = part + math.erf((math.log(stock_price / strike_price) + (rate + 0.5 * vol ** 2) * time_to_exp) / (vol * math.sqrt(time_to_exp)) / math.sqrt(2.0))
    option_value = option_value * part
    part_2 = strike_price * math.exp(-rate * time_to_exp) * 0.5
    part_3 = 1.0
    part_3 = part_3 + math.erf(((math.log(stock_price / strike_price) + (rate + 0.5 * vol ** 2) * time_to_exp) / (vol * math.sqrt(time_to_exp)) - vol * math.sqrt(time_to_exp)) / math.sqrt(2.0))
    part_2 = part_2 * part_3
    option_value = option_value - part_2
    return option_value

if __name__ == "__main__":
    val = black_scholes_call_approx(100.0, 100.0, 0.05, 0.2, 1.0)
    assert val > 0.0
