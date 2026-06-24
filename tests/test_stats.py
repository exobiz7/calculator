import pytest

from calc.modes import stats


def test_parse_list():
    assert stats.parse_list("1, 2, 3") == [1, 2, 3]
    assert stats.parse_list("1 2\n3 4") == [1, 2, 3, 4]


def test_describe_basic():
    d = stats.describe([2, 4, 4, 4, 5, 5, 7, 9])
    assert d["n"] == 8
    assert d["평균"] == pytest.approx(5)
    assert d["중앙값"] == pytest.approx(4.5)
    assert d["모표준편차"] == pytest.approx(2.0)
    assert d["표본표준편차"] == pytest.approx(2.13809, abs=1e-4)


def test_describe_single_value_omits_sample_stats():
    d = stats.describe([42])
    assert d["n"] == 1
    assert "표본표준편차" not in d  # needs n>=2


def test_describe_empty_raises():
    with pytest.raises(ValueError):
        stats.describe([])


def test_linreg():
    r = stats.linreg([1, 2, 3, 4], [2, 4, 6, 8])
    assert r["기울기"] == pytest.approx(2)
    assert r["절편"] == pytest.approx(0, abs=1e-9)
    assert r["상관계수 r"] == pytest.approx(1)


def test_normal():
    assert stats.normal_cdf(0) == pytest.approx(0.5)
    assert stats.normal_cdf(1.96) == pytest.approx(0.975, abs=1e-3)
    assert stats.normal_inv(0.975) == pytest.approx(1.96, abs=1e-3)
    assert stats.normal_pdf(0) == pytest.approx(0.3989423, abs=1e-6)


def test_binomial():
    assert stats.binom_pmf(2, 5, 0.5) == pytest.approx(0.3125)
    assert stats.binom_cdf(5, 5, 0.5) == pytest.approx(1.0)
    assert stats.binom_pmf(6, 5, 0.5) == 0.0  # k>n


def test_distribution_validation():
    with pytest.raises(ValueError):
        stats.normal_cdf(0, sigma=0)
    with pytest.raises(ValueError):
        stats.normal_inv(1.5)
