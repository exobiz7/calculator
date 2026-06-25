"""Headless UI smoke for the deterministic compute views.

For each view, invoking every button with empty entries must not raise an
uncaught Tk callback exception — empty/zero inputs should surface as an
"오류: ..." label instead (each view wraps its compute in try/except).

Scope is limited to deterministic views: ai/currency (network) and cas
(threading) are excluded because invoking their buttons performs I/O, and the
basic/scientific keypads follow a different (per-key) interaction model
covered by ``test_keypad_smoke``.

Shared ``app`` fixture and widget helpers live in ``conftest``.
"""

import pytest
import ttkbootstrap as ttk
from ui_smoke import iter_widgets

from calc.ui.analysis_view import AnalysisView
from calc.ui.financial_view import FinancialView
from calc.ui.kpi_view import KPIView
from calc.ui.stats_view import StatsView
from calc.ui.unit_view import UnitView

VIEW_CLASSES = [FinancialView, KPIView, UnitView, AnalysisView, StatsView]


@pytest.mark.parametrize("view_cls", VIEW_CLASSES, ids=lambda c: c.__name__)
def test_view_buttons_never_raise_with_empty_inputs(app, view_cls):
    app.smoke_errors.clear()

    views = [w for w in iter_widgets(app) if isinstance(w, view_cls)]
    assert views, f"no {view_cls.__name__} found in app"
    buttons = [b for v in views for b in iter_widgets(v) if isinstance(b, ttk.Button)]
    assert buttons, f"no buttons found in {view_cls.__name__}"

    for button in buttons:
        button.invoke()  # entries left empty/zero

    assert app.smoke_errors == [], (
        f"{view_cls.__name__} raised uncaught callback exceptions: "
        + ", ".join(f"{type(e).__name__}: {e}" for e in app.smoke_errors)
    )
