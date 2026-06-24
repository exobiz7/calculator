"""Statistics and probability distributions (standard library only).

Descriptive stats + simple linear regression via the `statistics` module, and
normal / binomial distributions via `math` (erf, comb). No external deps.
"""

import math
import statistics


def parse_list(text: str) -> list[float]:
    """Parse comma/space/newline separated numbers into a list of floats."""
    tokens = text.replace(",", " ").split()
    return [float(t) for t in tokens]


def describe(data: list[float]) -> dict:
    """Descriptive statistics. Sample-based items need n >= 2 (else omitted)."""
    if not data:
        raise ValueError("데이터가 비어 있습니다")
    n = len(data)
    out: dict[str, float | str] = {
        "n": n,
        "합계": sum(data),
        "평균": statistics.fmean(data),
        "중앙값": statistics.median(data),
        "최빈값": ", ".join(f"{m:g}" for m in statistics.multimode(data)),
        "최소": min(data),
        "최대": max(data),
        "범위": max(data) - min(data),
        "모분산": statistics.pvariance(data),
        "모표준편차": statistics.pstdev(data),
    }
    if n >= 2:
        out["표본분산"] = statistics.variance(data)
        out["표본표준편차"] = statistics.stdev(data)
        q1, q2, q3 = statistics.quantiles(data, n=4, method="inclusive")
        out["Q1"], out["Q3"], out["IQR"] = q1, q3, q3 - q1
    return out


def linreg(xs: list[float], ys: list[float]) -> dict:
    """Simple linear regression y = slope*x + intercept, with correlation r."""
    if len(xs) != len(ys):
        raise ValueError("x와 y 개수가 다릅니다")
    if len(xs) < 2:
        raise ValueError("점이 2개 이상 필요합니다")
    reg = statistics.linear_regression(xs, ys)
    return {
        "기울기": reg.slope,
        "절편": reg.intercept,
        "상관계수 r": statistics.correlation(xs, ys),
    }


# --- distributions ---------------------------------------------------------
def normal_pdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if sigma <= 0:
        raise ValueError("표준편차는 양수여야 합니다")
    return math.exp(-((x - mu) ** 2) / (2 * sigma**2)) / (
        sigma * math.sqrt(2 * math.pi)
    )


def normal_cdf(x: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    if sigma <= 0:
        raise ValueError("표준편차는 양수여야 합니다")
    return 0.5 * (1 + math.erf((x - mu) / (sigma * math.sqrt(2))))


def normal_inv(p: float, mu: float = 0.0, sigma: float = 1.0) -> float:
    """Inverse normal CDF (quantile) via bisection on the standard normal."""
    if not 0 < p < 1:
        raise ValueError("확률 p는 0과 1 사이여야 합니다")
    lo, hi = -40.0, 40.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if normal_cdf(mid) < p:
            lo = mid
        else:
            hi = mid
    return mu + sigma * (lo + hi) / 2


def binom_pmf(k: int, n: int, p: float) -> float:
    if not 0 <= p <= 1:
        raise ValueError("확률 p는 0과 1 사이여야 합니다")
    if k < 0 or k > n:
        return 0.0
    return math.comb(n, k) * p**k * (1 - p) ** (n - k)


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(binom_pmf(i, n, p) for i in range(0, min(k, n) + 1))
