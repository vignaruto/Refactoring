def requires_hazmat_label(item: dict[str, float], by_air: bool) -> bool:
    flash_point = item.get("flash_point_c", 100.0)
    volume = item.get("volume_l", 0.0)
    corrosive = bool(item.get("corrosive", False))
    sealed = bool(item.get("sealed", True))
    if (flash_point < 60.0 and volume > 1.0) or (corrosive and not sealed):
        return True
    if by_air and (flash_point < 93.0 or item.get("lithium_wh", 0.0) > 100.0):
        return True
    return False

if __name__ == "__main__":
    assert requires_hazmat_label({"flash_point_c": 20.0, "volume_l": 5.0}, False) is True
    assert requires_hazmat_label({"corrosive": True, "sealed": True}, False) is False
    assert requires_hazmat_label({"lithium_wh": 160.0}, True) is True
    assert requires_hazmat_label({"flash_point_c": 80.0, "volume_l": 2.0}, False) is False
