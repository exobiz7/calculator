# 실무 계산기 (Practical Calculator)

기본 / 공학용 / 회계·재무 세 가지 모드를 갖춘 Tkinter 데스크톱 계산기.
분야별 대표 상용 계산기(macOS 기본 · Casio fx-991 · HP 12C / Casio 비즈니스)를
벤치마킹했고, Anthropic 브랜드 팔레트 기반 라이트/다크 테마를 적용했다.

## 모드

- **기본** — 사칙연산, %, √, x², 1/x, 메모리(M+/M−/MR/MC), GT
- **공학용** — 삼각·쌍곡선·로그(logₐ)·지수, 거듭제곱·근, nPr/nCr·gcd/lcm, 상수(π·e·φ), 팩토리얼, 괄호 수식 입력(DEG/RAD), 즉석 결과·결과 형식(소수/분수/과학적/천단위)·수식 내 %·Ans/변수·복사
- **분석** — 수치 미분 `f'(x₀)`, 정적분 `∫ₐᵇ f dx`(심슨법), 방정식 근 `f(x)=0`(뉴턴+이분법)
- **통계** — 기술통계(평균·중앙값·분산·표준편차·사분위), 선형회귀(기울기·절편·r), 정규분포(pdf/cdf/역)·이항분포(pmf/cdf)
- **그래프** — `y=f(x)` 다중 플롯(색상별), x 범위 지정, 줌/팬(matplotlib 툴바), DEG/RAD. matplotlib 필요(없으면 자동 비활성)
- **CAS** — 기호수학: 간소화·전개·인수분해, 미분, 부정/정적분, 극한, 정확값(분수·√·π), S↔D(기호↔수치) 토글. sympy 필요(없으면 자동 비활성)
- **회계·재무** — 부가세(TAX±), 마진/마크업, 할인, TVM(n·i·PV·PMT·FV), 대출 상환표, 비례식
- **경영지표(KPI)** — 수익성(ROE·ROA·이익률)·안정성(부채·유동비율)·활동성(회전율·CCC)·시장가치(PER·PBR·EPS)·사업성(BEP·EVA·EBITDA·CAGR)·원가/단가 등 약 35종
- **단위환산** — 길이·무게·온도·면적·부피·시간·속도·데이터 + 압력·에너지·각도, 한국 전통 단위(평, 근·돈·관) 포함 (통화 환율 제외)
- **기록** — 모든 계산을 저장(`~/.calculator/history.json`)하고, 결과·계산식을 다시 불러와 재실행

라이트/다크 테마 토글(Anthropic 브랜드 팔레트) 지원.

## 실행

```bash
python main.py
```

> **주의 (macOS):** pyenv로 빌드한 Python에는 `_tkinter`가 없어 실행되지 않을 수 있다.
> 이 경우 tkinter가 포함된 Python(예: conda/miniforge)으로 실행한다:
> `/path/to/conda/bin/python main.py`

## 설치

```bash
pip install -r requirements.txt   # ttkbootstrap (런타임), pytest (개발)
```

## 테스트

```bash
python -m pytest
```

## 구조

```
calc/
├── core/      # 순수 로직: arithmetic, powers, ratio, memory, expr
├── modes/     # 모드별 엔진: basic, scientific, financial
└── ui/        # Tkinter(ttkbootstrap) 뷰 + 테마
main.py        # 진입점
tests/         # pytest
```

로직(순수 함수)과 UI를 분리해 로직은 단위 테스트로 검증하고, GUI는 수동 확인한다.
