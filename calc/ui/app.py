"""Tkinter application shell: a tabbed multi-mode calculator window.

Uses ttkbootstrap with a Claude/Anthropic-branded light/dark theme.
"""

import tkinter as tk

import ttkbootstrap as ttk

from calc.core.history import HistoryStore
from calc.ui.basic_view import BasicView
from calc.ui.financial_view import FinancialView
from calc.ui.history_view import HistoryView
from calc.ui.kpi_view import KPIView
from calc.ui.scientific_view import ScientificView
from calc.ui.unit_view import UnitView
from calc.ui.theme import (
    DARK,
    LIGHT,
    apply_overrides,
    configure_fonts,
    register_themes,
)


def build_app() -> ttk.Window:
    app = ttk.Window(themename="litera")
    register_themes(app.style)
    app.style.theme_use(LIGHT)
    apply_overrides(app.style)
    configure_fonts(app)
    app.title("실무 계산기")
    app.minsize(360, 520)

    # Header: title + theme toggle.
    header = ttk.Frame(app, padding=(12, 10, 12, 0))
    header.pack(fill="x")
    ttk.Label(header, text="실무 계산기", font=("Helvetica", 16, "bold")).pack(
        side="left"
    )

    theme_btn = ttk.Button(
        header, text="🌙 다크", bootstyle="secondary-outline", width=8
    )
    theme_btn.pack(side="right")

    def toggle_theme() -> None:
        if app.style.theme.name == LIGHT:
            app.style.theme_use(DARK)
            theme_btn.configure(text="☀ 라이트")
        else:
            app.style.theme_use(LIGHT)
            theme_btn.configure(text="🌙 다크")
        apply_overrides(app.style)

    theme_btn.configure(command=toggle_theme)

    history = HistoryStore()

    notebook = ttk.Notebook(app)
    basic = BasicView(
        notebook, on_record=lambda expr, res: history.record("기본", expr, res)
    )
    scientific = ScientificView(
        notebook, on_record=lambda expr, res: history.record("공학용", expr, res)
    )
    kpi = KPIView(
        notebook,
        on_record=lambda key, res, inputs: history.record("경영지표", key, res, inputs),
    )
    unit = UnitView(
        notebook,
        on_record=lambda expr, res, inputs: history.record(
            "단위환산", expr, res, inputs
        ),
    )
    notebook.add(basic, text="기본")
    notebook.add(scientific, text="공학용")
    notebook.add(FinancialView(notebook), text="회계·재무")
    notebook.add(kpi, text="경영지표")
    notebook.add(unit, text="단위환산")

    # History tab: re-load a past calculation into its mode.
    def load_entry(entry) -> None:
        if entry.mode == "경영지표":
            kpi.load(entry)
            notebook.select(kpi)
        elif entry.mode == "단위환산":
            unit.load(entry)
            notebook.select(unit)
        else:
            # Basic/scientific expressions re-load into the scientific entry field.
            scientific.load_expression(entry)
            notebook.select(scientific)

    history_view = HistoryView(notebook, store=history, on_load=load_entry)
    notebook.add(history_view, text="기록")
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    def on_tab_changed(event: tk.Event) -> None:
        if notebook.nametowidget(notebook.select()) is history_view:
            history_view.refresh()

    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    def dispatch_key(event: tk.Event) -> None:
        current = notebook.nametowidget(notebook.select())
        handler = getattr(current, "on_key", None)
        if handler is not None:
            handler(event)

    app.bind("<Key>", dispatch_key)
    return app


def run() -> None:
    build_app().mainloop()
