"""Shared fixtures for the headless UI smoke tests.

The ``app`` fixture builds the real application once per test module and routes
uncaught Tk callback exceptions into ``app.smoke_errors`` so tests can assert
that pressing buttons never surfaces an unhandled exception. Skips when no
display is available (e.g. headless CI without Tk).

Pure widget-tree helpers live in ``ui_smoke``.
"""

import tkinter as tk

import pytest

from calc.ui.app import build_app


@pytest.fixture(scope="module")
def app():
    try:
        instance = build_app()
    except tk.TclError as exc:  # no display available
        pytest.skip(f"Tk unavailable: {exc}")
    instance.smoke_errors = []
    instance.report_callback_exception = lambda exc, val, tb: (
        instance.smoke_errors.append(val)
    )
    yield instance
    instance.destroy()
