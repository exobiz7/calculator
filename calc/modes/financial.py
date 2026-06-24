"""Financial / accounting calculations.

Two families, benchmarked against commercial calculators:

- Korean business desk calculators (Casio): VAT (부가세), margin/markup, discount.
  Money is computed with :class:`decimal.Decimal` and rounded to the won.
- HP-12C style finance: time-value-of-money (n / i / PV / PMT / FV) and loan
  amortization schedules. These use float math (iterative where needed).
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

DEFAULT_VAT_RATE = 10  # 한국 부가가치세 기본 10%


def _money(value) -> Decimal:
    """Round a value to whole won (Decimal), half-up."""
    return Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Korean business: VAT (부가세)
# ---------------------------------------------------------------------------
@dataclass
class VatResult:
    supply: Decimal  # 공급가액
    vat: Decimal  # 세액
    total: Decimal  # 합계 (공급대가)


def add_vat(supply, rate: float = DEFAULT_VAT_RATE) -> VatResult:
    """공급가액 -> 부가세 포함 합계 (TAX+)."""
    supply_d = Decimal(str(supply))
    vat = _money(supply_d * Decimal(str(rate)) / 100)
    return VatResult(_money(supply_d), vat, _money(supply_d) + vat)


def remove_vat(total, rate: float = DEFAULT_VAT_RATE) -> VatResult:
    """부가세 포함 합계 -> 공급가액/세액 (TAX-)."""
    total_d = Decimal(str(total))
    supply = _money(total_d / (1 + Decimal(str(rate)) / 100))
    return VatResult(supply, _money(total_d) - supply, _money(total_d))


# ---------------------------------------------------------------------------
# Korean business: margin / markup / discount
# ---------------------------------------------------------------------------
def sell_from_cost_margin(cost, margin_rate: float):
    """원가 + 마진율(판매가 기준) -> 판매가. sell = cost / (1 - m)."""
    if margin_rate >= 100:
        raise ValueError("margin rate must be below 100%")
    return _money(Decimal(str(cost)) / (1 - Decimal(str(margin_rate)) / 100))


def sell_from_cost_markup(cost, markup_rate: float):
    """원가 + 마크업율(원가 기준) -> 판매가. sell = cost * (1 + m)."""
    return _money(Decimal(str(cost)) * (1 + Decimal(str(markup_rate)) / 100))


def cost_from_sell_margin(sell, margin_rate: float):
    """판매가 + 마진율 -> 원가. cost = sell * (1 - m)."""
    return _money(Decimal(str(sell)) * (1 - Decimal(str(margin_rate)) / 100))


def margin_rate(cost, sell) -> float:
    """마진율(판매가 기준) %."""
    if sell == 0:
        raise ValueError("selling price cannot be zero")
    return float((Decimal(str(sell)) - Decimal(str(cost))) / Decimal(str(sell)) * 100)


def markup_rate(cost, sell) -> float:
    """마크업율(원가 기준) %."""
    if cost == 0:
        raise ValueError("cost cannot be zero")
    return float((Decimal(str(sell)) - Decimal(str(cost))) / Decimal(str(cost)) * 100)


def apply_discount(price, discount_rate: float):
    """할인 적용가. price * (1 - d)."""
    return _money(Decimal(str(price)) * (1 - Decimal(str(discount_rate)) / 100))


# ---------------------------------------------------------------------------
# Time value of money (HP-12C style, END mode)
#   0 = pv*(1+i)^n + pmt*((1+i)^n - 1)/i + fv
#   rate is percent per period (I/Y); cash-flow sign convention applies.
# ---------------------------------------------------------------------------
def _grow(rate_pct: float, n: float) -> float:
    return (1 + rate_pct / 100) ** n


def tvm_fv(n: float, rate_pct: float, pv: float, pmt: float) -> float:
    i = rate_pct / 100
    g = _grow(rate_pct, n)
    if i == 0:
        return -(pv + pmt * n)
    return -(pv * g + pmt * (g - 1) / i)


def tvm_pv(n: float, rate_pct: float, pmt: float, fv: float) -> float:
    i = rate_pct / 100
    g = _grow(rate_pct, n)
    if i == 0:
        return -(fv + pmt * n)
    return -(fv + pmt * (g - 1) / i) / g


def tvm_pmt(n: float, rate_pct: float, pv: float, fv: float) -> float:
    i = rate_pct / 100
    g = _grow(rate_pct, n)
    if i == 0:
        return -(pv + fv) / n
    return -(pv * g + fv) * i / (g - 1)


def tvm_n(rate_pct: float, pv: float, pmt: float, fv: float) -> float:
    import math

    i = rate_pct / 100
    if i == 0:
        if pmt == 0:
            raise ValueError("cannot solve n with zero rate and zero payment")
        return -(pv + fv) / pmt
    a = pmt / i
    denom = pv + a
    numer = a - fv
    if denom == 0 or numer / denom <= 0:
        raise ValueError("no real solution for n with given inputs")
    return math.log(numer / denom) / math.log(1 + i)


def tvm_rate(
    n: float,
    pv: float,
    pmt: float,
    fv: float,
    guess: float = 1.0,
    tol: float = 1e-9,
    max_iter: int = 200,
) -> float:
    """Solve the periodic rate (%) by Newton's method with bisection fallback."""

    def f(rate_pct: float) -> float:
        i = rate_pct / 100
        if i == 0:
            return pv + pmt * n + fv
        g = _grow(rate_pct, n)
        return pv * g + pmt * (g - 1) / i + fv

    # Newton's method.
    rate = guess
    for _ in range(max_iter):
        f0 = f(rate)
        if abs(f0) < tol:
            return rate
        h = 1e-6
        deriv = (f(rate + h) - f(rate - h)) / (2 * h)
        if deriv == 0:
            break
        step = f0 / deriv
        rate -= step
        if abs(step) < tol:
            return rate
    # Bisection fallback over a wide bracket.
    lo, hi = -99.0, 1000.0
    flo, fhi = f(lo), f(hi)
    if flo * fhi > 0:
        raise ValueError("rate did not converge for given inputs")
    for _ in range(max_iter):
        mid = (lo + hi) / 2
        fm = f(mid)
        if abs(fm) < tol:
            return mid
        if flo * fm < 0:
            hi, fhi = mid, fm
        else:
            lo, flo = mid, fm
    return (lo + hi) / 2


# ---------------------------------------------------------------------------
# Loan amortization (원리금 균등상환)
# ---------------------------------------------------------------------------
@dataclass
class AmortRow:
    period: int
    payment: Decimal
    interest: Decimal
    principal: Decimal
    balance: Decimal


def amortization_schedule(
    principal, annual_rate_pct: float, months: int
) -> list[AmortRow]:
    """원리금 균등상환 스케줄. 월 이자율 = 연이율/12."""
    if months <= 0:
        raise ValueError("months must be positive")
    bal = Decimal(str(principal))
    r = Decimal(str(annual_rate_pct)) / 100 / 12
    if r == 0:
        payment = _money(bal / months)
    else:
        # P * r / (1 - (1+r)^-n)
        factor = (1 + r) ** (-months)
        payment = _money(bal * r / (1 - factor))

    rows: list[AmortRow] = []
    for period in range(1, months + 1):
        interest = _money(bal * r)
        if period == months:
            # Final period absorbs rounding so the balance lands on zero.
            principal_paid = bal
            pay = _money(bal + interest)
        else:
            principal_paid = payment - interest
            pay = payment
        bal = bal - principal_paid
        rows.append(
            AmortRow(period, _money(pay), interest, _money(principal_paid), _money(bal))
        )
    return rows
