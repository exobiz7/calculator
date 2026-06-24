"""Tkinter application shell: a tabbed multi-mode calculator window."""

import tkinter as tk
from tkinter import ttk

from calc.ui.basic_view import BasicView
from calc.ui.financial_view import FinancialView
from calc.ui.scientific_view import ScientificView


def build_app() -> tk.Tk:
    root = tk.Tk()
    root.title("실무 계산기")
    root.minsize(320, 440)

    notebook = ttk.Notebook(root)
    notebook.add(BasicView(notebook), text="기본")
    notebook.add(ScientificView(notebook), text="공학용")
    notebook.add(FinancialView(notebook), text="회계·재무")
    notebook.pack(fill="both", expand=True)

    def dispatch_key(event: tk.Event) -> None:
        current = notebook.nametowidget(notebook.select())
        handler = getattr(current, "on_key", None)
        if handler is not None:
            handler(event)

    root.bind("<Key>", dispatch_key)
    return root


def run() -> None:
    build_app().mainloop()
