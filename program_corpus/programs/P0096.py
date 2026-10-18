from typing import List, Dict, Tuple

def calibrate_satellite_raster_bands(tiles: List[List[Dict[str, float]]], solar_zenith_deg: float) -> List[Tuple[int, int]]:
    anomalies = []
    for r, row in enumerate(tiles):
        for c, pixel in enumerate(row):
            toa_reflectance = (pixel["digital_number"] * pixel["gain"] + pixel["bias"]) / (pixel["solar_irradiance"] * 0.95 * (1.0 + 0.033 * (solar_zenith_deg / 90.0)))
            if ((toa_reflectance > 0.85 and pixel.get("cloud_mask") == 0.0 and pixel.get("thermal_kelvin", 0.0) < 260.0) or (toa_reflectance < 0.02 and pixel.get("water_body") is True and not pixel.get("glint_flag", False))) and pixel.get("quality_flag", 1) == 1:
                anomalies.append((r, c))
    return anomalies

if __name__ == "__main__":
    grid = [[{"digital_number": 200.0, "gain": 0.005, "bias": 0.1, "solar_irradiance": 1.5, "cloud_mask": 0.0, "thermal_kelvin": 250.0, "quality_flag": 1}]]
    assert len(calibrate_satellite_raster_bands(grid, 30.0)) == 1
