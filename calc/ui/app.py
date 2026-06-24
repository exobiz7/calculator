"""Tkinter application shell: a tabbed multi-mode calculator window.

Uses ttkbootstrap with a Claude/Anthropic-branded light/dark theme.
"""

import tkinter as tk

import ttkbootstrap as ttk

from calc.ui.basic_view import BasicView
from calc.ui.financial_view import FinancialView
from calc.ui.scientific_view import ScientificView
from calc.ui.theme import DARK, LIGHT, configure_fonts, register_themes


def build_app() -> ttk.Window:
    app = ttk.Window(themename="litera")
    register_themes(app.style)
    app.style.theme_use(LIGHT)
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

    theme_btn.configure(command=toggle_theme)

    notebook = ttk.Notebook(app)
    notebook.add(BasicView(notebook), text="기본")
    notebook.add(ScientificView(notebook), text="공학용")
    notebook.add(FinancialView(notebook), text="회계·재무")
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    def dispatch_key(event: tk.Event) -> None:
        current = notebook.nametowidget(notebook.select())
        handler = getattr(current, "on_key", None)
        if handler is not None:
            handler(event)

    app.bind("<Key>", dispatch_key)
    return app


def run() -> None:
    build_app().mainloop()
