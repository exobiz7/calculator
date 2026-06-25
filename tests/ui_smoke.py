"""Pure widget-tree helpers shared by the headless UI smoke tests.

Kept separate from ``conftest`` (which holds only fixtures) so tests can import
these without importing the conftest module directly. Not collected by pytest
(the filename does not match ``test_*``).
"""

import ttkbootstrap as ttk


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
