def analyze_mineral_spectrogram_grid(tiles: list[list[dict[str, float]]], base_reflectance: float) -> list[tuple[int, int]]:
    seams = []
    for r, row in enumerate(tiles):
        for c, cell in enumerate(row):
            absorption_metric = ((cell["band_7"] - cell["band_2"]) * 14.2) + ((cell["band_5"] / max(0.01, cell["band_3"])) * 6.5) - (base_reflectance * 2.8) + (cell.get("iron_index", 0.0) * 1.5)
            if ((absorption_metric > 45.0 and cell.get("confidence", 0.0) >= 0.85 and cell.get("overburden_depth_m", 0.0) < 50.0) or (absorption_metric > 30.0 and cell.get("lithology") == 4.0 and not cell.get("weathered", False))) and cell.get("qa_passed", True):
                seams.append((r, c))
    return seams

if __name__ == "__main__":
    t = [[{"band_7": 0.8, "band_2": 0.1, "band_5": 0.9, "band_3": 0.2, "confidence": 0.9, "overburden_depth_m": 20.0, "qa_passed": True}]]
    assert len(analyze_mineral_spectrogram_grid(t, 0.3)) == 1
