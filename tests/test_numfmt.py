from calc.core.numfmt import MODES, format_value


def test_auto():
    assert format_value(5.0, "자동") == "5"
    assert format_value(2.5, "자동") == "2.5"


def test_thousands():
    assert format_value(1234567.0, "천단위") == "1,234,567"
    assert format_value(1234.5, "천단위") == "1,234.5"


def test_fraction():
    assert format_value(0.5, "분수") == "1/2"
    assert format_value(0.75, "분수") == "3/4"
    assert format_value(4.0, "분수") == "4"


def test_scientific():
    assert format_value(12345.0, "과학적") == "1.234500e+04"


def test_unknown_mode_falls_back_to_auto():
    assert format_value(5.0, "???") == "5"


def test_modes_list():
    assert "분수" in MODES and "과학적" in MODES
