"""Headless UI smoke for the 회계·재무 view.

Invoking every button with empty entries must not raise an uncaught Tk
callback exception — empty/zero inputs should surface as a "오류: ..." label
instead (see :mod:`calc.ui.financial_view`). Skips when no display is
available (e.g. headless CI without Tk).
"""

import tkinter as tk

import pytest
import ttkbootstrap as ttk

from calc.ui.app import build_app
from calc.ui.financial_view import FinancialView


def _iter_widgets(widget):
    yield widget
    for child in widget.winfo_children():
        yield from _iter_widgets(child)


def test_financial_view_buttons_never_raise_with_empty_inputs():
    try:
        app = build_app()
    except tk.TclError as exc:  # no display available
        pytest.skip(f"Tk unavailable: {exc}")

    errors: list[BaseException] = []
    app.report_callback_exception = lambda exc, val, tb: errors.append(val)

    try:
        buttons = [
            w
            for fv in _iter_widgets(app)
            if isinstance(fv, FinancialView)
            for w in _iter_widgets(fv)
            if isinstance(w, ttk.Button)
        ]
        assert buttons, "no buttons found in FinancialView"

        for button in buttons:
            button.invoke()  # entries left empty/zero
    finally:
        app.destroy()

    assert errors == [], "uncaught callback exceptions: " + ", ".join(
        f"{type(e).__name__}: {e}" for e in errors
    )
