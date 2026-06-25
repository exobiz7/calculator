"""Shared fixtures and helpers for the headless UI smoke tests.

The ``app`` fixture builds the real application once per test module and routes
uncaught Tk callback exceptions into ``app.smoke_errors`` so tests can assert
that pressing buttons never surfaces an unhandled exception. Skips when no
display is available (e.g. headless CI without Tk).
"""

import tkinter as tk

import pytest
import ttkbootstrap as ttk

from calc.ui.app import build_app


def iter_widgets(widget):
    """Depth-first walk over ``widget`` and all of its descendants."""
    yield widget
    for child in widget.winfo_children():
        yield from iter_widgets(child)


def find_view(app, view_cls):
    """Return the first widget of type ``view_cls`` in the app tree."""
    for widget in iter_widgets(app):
        if isinstance(widget, view_cls):
            return widget
    raise AssertionError(f"no {view_cls.__name__} found in app")


def buttons_by_label(view):
    """Map each button's visible text to its widget within ``view``."""
    return {b.cget("text"): b for b in iter_widgets(view) if isinstance(b, ttk.Button)}


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
