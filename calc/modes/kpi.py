"""Financial / managerial-accounting KPI registry.

Each KPI is a data row: inputs (variable, label) + a formula string evaluated by
the shared safe_eval. Adding a metric = adding one KPI() entry — no new code.
"""

from dataclasses import dataclass

from calc.core.expr import safe_eval


@dataclass(frozen=True)
class KPI:
    key: str
    name: str
    category: str
    inputs: tuple[tuple[str, str], ...]  # (variable, label)
    formula: str
    unit: str = ""
    note: str = ""

    @property
    def variables(self) -> list[str]:
        return [v for v, _ in self.inputs]


def compute(kpi: KPI, values: dict) -> float:
    """Evaluate a KPI's formula with the given variable values."""
    return float(safe_eval(kpi.formula, variables=values))


# Category display order
CATEGORIES = ["수익성", "안정성", "활동성", "시장가치", "사업성/투자", "원가/단가"]

KPIS: list[KPI] = [
    # --- 수익성 ---------------------------------------------------------
    KPI(
        "gpm",
        "매출총이익률",
        "수익성",
        (("gross", "매출총이익"), ("revenue", "매출액")),
        "gross/revenue*100",
        "%",
    ),
    KPI(
        "opm",
        "영업이익률",
        "수익성",
        (("op_income", "영업이익"), ("revenue", "매출액")),
        "op_income/revenue*100",
        "%",
    ),
    KPI(
        "npm",
        "순이익률",
        "수익성",
        (("net_income", "당기순이익"), ("revenue", "매출액")),
        "net_income/revenue*100",
        "%",
    ),
    KPI(
        "roa",
        "ROA (총자산이익률)",
        "수익성",
        (("net_income", "당기순이익"), ("assets", "총자산")),
        "net_income/assets*100",
        "%",
    ),
    KPI(
        "roe",
        "ROE (자기자본이익률)",
        "수익성",
        (("net_income", "당기순이익"), ("equity", "자기자본")),
        "net_income/equity*100",
        "%",
    ),
    KPI(
        "roic",
        "ROIC (투하자본이익률)",
        "수익성",
        (("nopat", "세후영업이익"), ("invested_capital", "투하자본")),
        "nopat/invested_capital*100",
        "%",
    ),
    # --- 안정성 ---------------------------------------------------------
    KPI(
        "debt_ratio",
        "부채비율",
        "안정성",
        (("debt", "부채총계"), ("equity", "자기자본")),
        "debt/equity*100",
        "%",
    ),
    KPI(
        "current_ratio",
        "유동비율",
        "안정성",
        (("current_assets", "유동자산"), ("current_liabilities", "유동부채")),
        "current_assets/current_liabilities*100",
        "%",
    ),
    KPI(
        "quick_ratio",
        "당좌비율",
        "안정성",
        (("quick_assets", "당좌자산"), ("current_liabilities", "유동부채")),
        "quick_assets/current_liabilities*100",
        "%",
    ),
    KPI(
        "equity_ratio",
        "자기자본비율",
        "안정성",
        (("equity", "자기자본"), ("assets", "총자산")),
        "equity/assets*100",
        "%",
    ),
    KPI(
        "interest_coverage",
        "이자보상배율",
        "안정성",
        (("op_income", "영업이익"), ("interest", "이자비용")),
        "op_income/interest",
        "배",
    ),
    # --- 활동성 ---------------------------------------------------------
    KPI(
        "asset_turnover",
        "총자산회전율",
        "활동성",
        (("revenue", "매출액"), ("assets", "총자산")),
        "revenue/assets",
        "회",
    ),
    KPI(
        "inventory_turnover",
        "재고자산회전율",
        "활동성",
        (("cogs", "매출원가"), ("inventory", "평균재고")),
        "cogs/inventory",
        "회",
    ),
    KPI(
        "dio",
        "재고일수 (DIO)",
        "활동성",
        (("inventory", "평균재고"), ("cogs", "매출원가")),
        "inventory/cogs*365",
        "일",
    ),
    KPI(
        "dso",
        "매출채권회수일수 (DSO)",
        "활동성",
        (("receivables", "매출채권"), ("revenue", "매출액")),
        "receivables/revenue*365",
        "일",
    ),
    KPI(
        "dpo",
        "매입채무지급일수 (DPO)",
        "활동성",
        (("payables", "매입채무"), ("cogs", "매출원가")),
        "payables/cogs*365",
        "일",
    ),
    KPI(
        "ccc",
        "현금전환주기 (CCC)",
        "활동성",
        (("dso", "DSO(일)"), ("dio", "DIO(일)"), ("dpo", "DPO(일)")),
        "dso+dio-dpo",
        "일",
    ),
    # --- 시장가치 -------------------------------------------------------
    KPI(
        "eps",
        "EPS (주당순이익)",
        "시장가치",
        (("net_income", "당기순이익"), ("shares", "발행주식수")),
        "net_income/shares",
        "원",
    ),
    KPI(
        "bps",
        "BPS (주당순자산)",
        "시장가치",
        (("equity", "자기자본"), ("shares", "발행주식수")),
        "equity/shares",
        "원",
    ),
    KPI(
        "per",
        "PER (주가수익비율)",
        "시장가치",
        (("price", "주가"), ("eps", "EPS")),
        "price/eps",
        "배",
    ),
    KPI(
        "pbr",
        "PBR (주가순자산비율)",
        "시장가치",
        (("price", "주가"), ("bps", "BPS")),
        "price/bps",
        "배",
    ),
    KPI(
        "ev_ebitda",
        "EV/EBITDA",
        "시장가치",
        (("ev", "기업가치(EV)"), ("ebitda", "EBITDA")),
        "ev/ebitda",
        "배",
    ),
    KPI(
        "psr",
        "PSR (주가매출비율)",
        "시장가치",
        (("market_cap", "시가총액"), ("revenue", "매출액")),
        "market_cap/revenue",
        "배",
    ),
    KPI(
        "div_yield",
        "배당수익률",
        "시장가치",
        (("dps", "주당배당금"), ("price", "주가")),
        "dps/price*100",
        "%",
    ),
    KPI(
        "payout",
        "배당성향",
        "시장가치",
        (("dividends", "배당금총액"), ("net_income", "당기순이익")),
        "dividends/net_income*100",
        "%",
    ),
    # --- 사업성/투자 ----------------------------------------------------
    KPI(
        "bep",
        "손익분기점 (수량)",
        "사업성/투자",
        (
            ("fixed_cost", "고정비"),
            ("price", "단위판매가"),
            ("variable_cost", "단위변동비"),
        ),
        "fixed_cost/(price-variable_cost)",
        "개",
    ),
    KPI(
        "contribution",
        "공헌이익",
        "사업성/투자",
        (("price", "단위판매가"), ("variable_cost", "단위변동비")),
        "price-variable_cost",
        "원",
    ),
    KPI(
        "contribution_margin",
        "공헌이익률",
        "사업성/투자",
        (("price", "단위판매가"), ("variable_cost", "단위변동비")),
        "(price-variable_cost)/price*100",
        "%",
    ),
    KPI(
        "margin_of_safety",
        "안전한계율",
        "사업성/투자",
        (("sales", "실제매출"), ("bep_sales", "손익분기매출")),
        "(sales-bep_sales)/sales*100",
        "%",
    ),
    KPI(
        "ebitda",
        "EBITDA",
        "사업성/투자",
        (
            ("op_income", "영업이익"),
            ("depreciation", "감가상각비"),
            ("amortization", "무형상각비"),
        ),
        "op_income+depreciation+amortization",
        "원",
    ),
    KPI(
        "eva",
        "EVA (경제적부가가치)",
        "사업성/투자",
        (("nopat", "세후영업이익"), ("capital", "투하자본"), ("wacc", "WACC(%)")),
        "nopat-(capital*wacc/100)",
        "원",
    ),
    KPI(
        "roi",
        "ROI (투자수익률)",
        "사업성/투자",
        (("gain", "투자이익"), ("cost", "투자원금")),
        "gain/cost*100",
        "%",
    ),
    KPI(
        "payback",
        "투자회수기간",
        "사업성/투자",
        (("investment", "투자액"), ("annual_cashflow", "연현금흐름")),
        "investment/annual_cashflow",
        "년",
    ),
    KPI(
        "cagr",
        "CAGR (연평균성장률)",
        "사업성/투자",
        (("begin", "기초값"), ("end", "기말값"), ("years", "기간(년)")),
        "((end/begin)**(1/years)-1)*100",
        "%",
    ),
    # --- 원가/단가 ------------------------------------------------------
    KPI(
        "markup_price",
        "원가가산 단가",
        "원가/단가",
        (("cost", "원가"), ("markup_rate", "가산율(%)")),
        "cost*(1+markup_rate/100)",
        "원",
    ),
    KPI(
        "target_margin_price",
        "목표이익 단가",
        "원가/단가",
        (("cost", "원가"), ("margin_rate", "목표마진율(%)")),
        "cost/(1-margin_rate/100)",
        "원",
    ),
]

KPI_BY_KEY = {k.key: k for k in KPIS}


def by_category(category: str) -> list[KPI]:
    return [k for k in KPIS if k.category == category]
