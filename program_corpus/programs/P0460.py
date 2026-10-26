import math

def survey_sample_size(proportion: float, margin: float, population: int, z: float = 1.96) -> int:
    infinite_size = (z ** 2) * proportion * (1.0 - proportion) / (margin ** 2)
    adjusted_size = infinite_size / (1.0 + (infinite_size - 1.0) / population)
    return math.ceil(adjusted_size)

if __name__ == "__main__":
    assert survey_sample_size(0.5, 0.05, 10 ** 9) == 385
    assert survey_sample_size(0.5, 0.05, 1000) == 278
