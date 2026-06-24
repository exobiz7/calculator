import pytest

from calc.modes import units
from calc.modes.units import CATEGORY_BY_KEY, convert


def _conv(cat_key, value, src, dst):
    cat = CATEGORY_BY_KEY[cat_key]
    return convert(value, cat.unit(src), cat.unit(dst))


def test_length():
    assert _conv("length", 1, "km", "m") == pytest.approx(1000)
    assert _conv("length", 1, "mi", "km") == pytest.approx(1.609344)
    assert _conv("length", 12, "in", "ft") == pytest.approx(1)


def test_mass_and_korean_units():
    assert _conv("mass", 1, "kg", "g") == pytest.approx(1000)
    assert _conv("mass", 1, "근(600g)", "g") == pytest.approx(600)
    assert _conv("mass", 1, "관", "kg") == pytest.approx(3.75)
    assert _conv("mass", 1, "돈", "g") == pytest.approx(3.75)


def test_temperature_offsets():
    assert _conv("temperature", 100, "°C", "°F") == pytest.approx(212)
    assert _conv("temperature", 32, "°F", "°C") == pytest.approx(0)
    assert _conv("temperature", 0, "°C", "K") == pytest.approx(273.15)
    assert _conv("temperature", 300, "K", "°C") == pytest.approx(26.85)


def test_area_pyeong():
    assert _conv("area", 1, "평", "m²") == pytest.approx(3.3057851)
    assert _conv("area", 1, "ha", "m²") == pytest.approx(10000)


def test_data_binary():
    assert _conv("data", 1, "GB", "MB") == pytest.approx(1024)
    assert _conv("data", 1, "B", "bit") == pytest.approx(8)


def test_speed_pressure_energy_angle():
    assert _conv("speed", 36, "km/h", "m/s") == pytest.approx(10)
    assert _conv("pressure", 1, "atm", "Pa") == pytest.approx(101325)
    assert _conv("energy", 1, "kcal", "cal") == pytest.approx(1000)
    assert _conv("angle", 180, "°", "rad") == pytest.approx(3.14159265, abs=1e-6)


def test_roundtrip_all_categories():
    # value -> other unit -> back should be identity for every unit pair
    for cat in units.CATEGORIES:
        base = cat.units[0]
        for u in cat.units:
            back = convert(convert(7.0, base, u), u, base)
            assert back == pytest.approx(7.0)


def test_unknown_unit_raises():
    with pytest.raises(ValueError):
        CATEGORY_BY_KEY["length"].unit("parsec")
