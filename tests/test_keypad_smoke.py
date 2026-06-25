"""Headless UI smoke for the basic / scientific keypads.

The keypads differ from the single-button compute views: keys mutate engine
state (or an expression that is live-evaluated on every keystroke), and "="
forces an evaluation. Pressing arbitrary key sequences — including ones that
provoke math errors (divide-by-zero, incomplete expressions, domain errors) —
and then "=" must never raise an uncaught Tk callback exception; the engines
surface errors via their own state instead.

Shared ``app`` fixture and widget helpers live in ``conftest``.
"""

import pytest
import ttkbootstrap as ttk
from ui_smoke import buttons_by_label, find_view, iter_widgets

from calc.ui.basic_view import BasicView
from calc.ui.scientific_view import ScientificView

# Per-view "clear everything" key label, pressed before each sequence so cases
# do not leak state through the shared (module-scoped) app.
CLEAR_LABEL = {BasicView: "AC", ScientificView: "C"}

# (view_cls, key-label sequence) — each sequence is followed by "=".
ADVERSARIAL = [
    (BasicView, ["1", "÷", "0"]),  # divide by zero
    (BasicView, ["0", "1/x"]),  # reciprocal of zero
    (BasicView, ["√"]),  # sqrt of current value
    (BasicView, ["7", "%"]),  # percent with no pending op
    (BasicView, ["±"]),  # negate empty
    (BasicView, ["9", "9", "9", "×", "9", "9", "9"]),  # large product
    (ScientificView, ["1", "÷", "0"]),  # divide by zero
    (ScientificView, ["√"]),  # "sqrt(" — incomplete
    (ScientificView, ["n!"]),  # "fact(" — incomplete
    (ScientificView, ["("]),  # unbalanced paren
    (ScientificView, ["ln", "0", ")"]),  # ln(0)
    (ScientificView, ["asin", "9", "9", ")"]),  # asin(99) — domain error
    (ScientificView, ["1", ".", ".", "2"]),  # malformed number
    (ScientificView, ["sin", "cos", "tan"]),  # nested incomplete calls
]

KEYPAD_VIEWS = [BasicView, ScientificView]


@pytest.mark.parametrize("view_cls", KEYPAD_VIEWS, ids=lambda c: c.__name__)
def test_keypad_press_every_key_then_equals(app, view_cls):
    """Pressing every key once, then '=', must not raise."""
    app.smoke_errors.clear()
    view = find_view(app, view_cls)
    buttons = [b for b in iter_widgets(view) if isinstance(b, ttk.Button)]
    assert buttons, f"no buttons in {view_cls.__name__}"

    for button in buttons:
        button.invoke()
    buttons_by_label(view)["="].invoke()

    assert app.smoke_errors == [], f"{view_cls.__name__} raised: " + ", ".join(
        f"{type(e).__name__}: {e}" for e in app.smoke_errors
    )


@pytest.mark.parametrize(
    "view_cls,sequence",
    ADVERSARIAL,
    ids=lambda v: v.__name__ if isinstance(v, type) else "-".join(v),
)
def test_keypad_adversarial_sequence_then_equals(app, view_cls, sequence):
    """Error-provoking sequences followed by '=' must not raise."""
    app.smoke_errors.clear()
    view = find_view(app, view_cls)
    keys = buttons_by_label(view)

    keys[CLEAR_LABEL[view_cls]].invoke()  # reset shared state
    for label in sequence:
        keys[label].invoke()
    keys["="].invoke()

    assert app.smoke_errors == [], (
        f"{view_cls.__name__} {sequence} raised: "
        + ", ".join(f"{type(e).__name__}: {e}" for e in app.smoke_errors)
    )
