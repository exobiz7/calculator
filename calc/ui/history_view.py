"""Tkinter view: calculation history with re-use."""

import tkinter as tk

import ttkbootstrap as ttk


class HistoryView(ttk.Frame):
    """Lists recent calculations; can re-load an entry's formula into its mode."""

    def __init__(self, master: tk.Misc, store, on_load=None) -> None:
        super().__init__(master, padding=10)
        self.store = store
        self._on_load = on_load  # callable(entry) -> None
        self._entries: list = []
        self._build()
        self.refresh()

    def _build(self) -> None:
        bar = ttk.Frame(self)
        bar.pack(fill="x", pady=(0, 8))
        ttk.Button(
            bar, text="새로고침", bootstyle="secondary-outline", command=self.refresh
        ).pack(side="left", padx=2)
        ttk.Button(
            bar, text="불러오기", bootstyle="primary", command=self._load_selected
        ).pack(side="left", padx=2)
        ttk.Button(
            bar, text="전체삭제", bootstyle="danger-outline", command=self._clear
        ).pack(side="right", padx=2)

        cols = ("시각", "모드", "식", "결과")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=14)
        widths = {"시각": 130, "모드": 70, "식": 220, "결과": 110}
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=widths[c], anchor="w")
        self.tree.column("결과", anchor="e")
        self.tree.pack(side="left", fill="both", expand=True)
        sb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        sb.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<Double-1>", lambda e: self._load_selected())

    def refresh(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.tree.tag_configure("date", background="", foreground="#888")
        self._entries = self.store.recent()
        last_date = None
        for i, e in enumerate(self._entries):
            date = e.timestamp[:10]
            if date != last_date:
                self.tree.insert(
                    "",
                    "end",
                    iid=f"d{date}",
                    tags=("date",),
                    values=(f"── {date} ──", "", "", ""),
                )
                last_date = date
            time = e.timestamp[11:19]  # date shown in the group header
            self.tree.insert(
                "", "end", iid=f"e{i}", values=(time, e.mode, e.expression, e.result)
            )

    def _selected_entry(self):
        sel = self.tree.selection()
        if not sel or not sel[0].startswith("e"):
            return None  # ignore date-header rows
        return self._entries[int(sel[0][1:])]

    def _load_selected(self) -> None:
        entry = self._selected_entry()
        if entry is not None and self._on_load:
            self._on_load(entry)

    def _clear(self) -> None:
        self.store.clear()
        self.refresh()

    def on_key(self, event: tk.Event) -> None:
        return
