"""Unit conversion registry.

Each category converts via a base unit. Most units are linear (a factor to the
base); temperature is special (offset), so each Unit carries to_base/from_base
callables. Includes Korean traditional units (면적 평; 무게 근·돈·관). Currency
is intentionally excluded (needs live rates → separate, gated feature).
"""

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Unit:
    name: str
    to_base: Callable[[float], float]
    from_base: Callable[[float], float]


@dataclass(frozen=True)
class Category:
    key: str
    name: str
    units: tuple[Unit, ...]

    def unit(self, name: str) -> Unit:
        for u in self.units:
            if u.name == name:
                return u
        raise ValueError(f"unknown unit: {name}")

    @property
    def unit_names(self) -> list[str]:
        return [u.name for u in self.units]


def convert(value: float, src: Unit, dst: Unit) -> float:
    """Convert value from src unit to dst unit (via the category base unit)."""
    return dst.from_base(src.to_base(value))


def _lin(pairs: list[tuple[str, float]]) -> tuple[Unit, ...]:
    """Build linear units from (name, factor-to-base) pairs."""
    return tuple(
        Unit(name, (lambda x, f=f: x * f), (lambda x, f=f: x / f)) for name, f in pairs
    )


# --- categories ------------------------------------------------------------
CATEGORIES: list[Category] = [
    Category(
        "length",
        "길이",
        _lin(
            [
                ("mm", 0.001),
                ("cm", 0.01),
                ("m", 1.0),
                ("km", 1000.0),
                ("in", 0.0254),
                ("ft", 0.3048),
                ("yd", 0.9144),
                ("mi", 1609.344),
            ]
        ),
    ),  # base: meter
    Category(
        "mass",
        "무게",
        _lin(
            [
                ("mg", 0.001),
                ("g", 1.0),
                ("kg", 1000.0),
                ("t(톤)", 1_000_000.0),
                ("oz", 28.349523125),
                ("lb", 453.59237),
                ("돈", 3.75),
                ("근(600g)", 600.0),
                ("관", 3750.0),  # 한국 전통
            ]
        ),
    ),  # base: gram
    Category(
        "temperature",
        "온도",
        (
            Unit("°C", lambda x: x, lambda x: x),
            Unit("°F", lambda x: (x - 32) * 5 / 9, lambda x: x * 9 / 5 + 32),
            Unit("K", lambda x: x - 273.15, lambda x: x + 273.15),
        ),
    ),  # base: Celsius
    Category(
        "area",
        "면적",
        _lin(
            [
                ("cm²", 0.0001),
                ("m²", 1.0),
                ("km²", 1_000_000.0),
                ("a(아르)", 100.0),
                ("ha", 10000.0),
                ("ft²", 0.09290304),
                ("acre", 4046.8564224),
                ("평", 3.3057851),  # 한국 전통 (1평 ≈ 3.3058㎡)
            ]
        ),
    ),  # base: m²
    Category(
        "volume",
        "부피",
        _lin(
            [
                ("mL", 0.001),
                ("L", 1.0),
                ("m³", 1000.0),
                ("cm³", 0.001),
                ("gal(US)", 3.785411784),
                ("qt(US)", 0.946352946),
            ]
        ),
    ),  # base: liter
    Category(
        "time",
        "시간",
        _lin(
            [
                ("ms", 0.001),
                ("s", 1.0),
                ("min", 60.0),
                ("h", 3600.0),
                ("day", 86400.0),
                ("week", 604800.0),
            ]
        ),
    ),  # base: second
    Category(
        "speed",
        "속도",
        _lin(
            [
                ("m/s", 1.0),
                ("km/h", 0.2777777778),
                ("mph", 0.44704),
                ("knot", 0.5144444444),
                ("ft/s", 0.3048),
            ]
        ),
    ),  # base: m/s
    Category(
        "data",
        "데이터",
        _lin(
            [
                ("bit", 0.125),
                ("B", 1.0),
                ("KB", 1024.0),
                ("MB", 1024.0**2),
                ("GB", 1024.0**3),
                ("TB", 1024.0**4),
            ]
        ),
    ),  # base: byte (binary 1024)
    Category(
        "pressure",
        "압력",
        _lin(
            [
                ("Pa", 1.0),
                ("kPa", 1000.0),
                ("bar", 100000.0),
                ("atm", 101325.0),
                ("psi", 6894.757293),
                ("mmHg", 133.322387415),
            ]
        ),
    ),  # base: pascal
    Category(
        "energy",
        "에너지",
        _lin(
            [
                ("J", 1.0),
                ("kJ", 1000.0),
                ("cal", 4.184),
                ("kcal", 4184.0),
                ("Wh", 3600.0),
                ("kWh", 3_600_000.0),
            ]
        ),
    ),  # base: joule
    Category(
        "angle",
        "각도",
        _lin(
            [
                ("°", 1.0),
                ("rad", 57.29577951308232),
                ("grad", 0.9),
            ]
        ),
    ),  # base: degree
]

CATEGORY_BY_KEY = {c.key: c for c in CATEGORIES}
