"""Tkinter view for live currency conversion (Frankfurter / ECB rates)."""

import threading
import tkinter as tk

import ttkbootstrap as ttk

from calc.core import forex
from calc.core.numfmt import format_value


def _f(text: str, default: float = 0.0) -> float:
    text = text.replace(",", "").strip()
    return float(text) if text else default


class CurrencyView(ttk.Frame):
    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self._on_record = on_record
        self._amount = tk.StringVar(value="1")
        self._result = tk.StringVar(value="")
        self._status = tk.StringVar(value="")
        self._build()
        self._populate_codes()  # from disk cache if present (instant)
        self._refresh()  # background: fetch latest

    def _build(self) -> None:
        row = ttk.Frame(self)
        row.pack(fill="x")
        ttk.Label(row, text="금액").grid(row=0, column=0, sticky="w")
        e = ttk.Entry(row, textvariable=self._amount, width=14, font=("Helvetica", 14))
        e.grid(row=0, column=1, sticky="we", padx=6)
        e.bind("<Return>", lambda ev: self._convert())
        self._from = ttk.Combobox(row, state="readonly", width=8)
        self._from.grid(row=0, column=2, padx=2)
        ttk.Button(
            row, text="⇄", width=3, bootstyle="secondary-outline", command=self._swap
        ).grid(row=0, column=3, padx=2)
        self._to = ttk.Combobox(row, state="readonly", width=8)
        self._to.grid(row=0, column=4, padx=2)
        row.columnconfigure(1, weight=1)

        btns = ttk.Frame(self)
        btns.pack(fill="x", pady=4)
        ttk.Button(btns, text="환산", bootstyle="primary", command=self._convert).pack(
            side="left", fill="x", expand=True
        )
        ttk.Button(
            btns, text="갱신", width=6, bootstyle="info", command=self._refresh
        ).pack(side="left", padx=(6, 0))

        ttk.Label(
            self,
            textvariable=self._result,
            bootstyle="success",
            font=("Helvetica", 20, "bold"),
        ).pack(anchor="w", pady=(6, 0))
        ttk.Label(self, textvariable=self._status, bootstyle="secondary").pack(
            anchor="w"
        )

    # --- data -----------------------------------------------------------
    def _populate_codes(self) -> None:
        codes = forex.cached_codes()  # no network — background _refresh fills in
        if not codes:
            return
        self._from.configure(values=codes)
        self._to.configure(values=codes)
        if not self._from.get():
            self._from.set("USD" if "USD" in codes else codes[0])
        if not self._to.get():
            self._to.set("KRW" if "KRW" in codes else codes[-1])

    def _update_status(self) -> None:
        date, fetched = forex.info()
        if date:
            self._status.set(
                f"기준일 {date} · 갱신 {fetched[:16].replace('T', ' ')} "
                f"(ECB/Frankfurter, 일 1회)"
            )
        else:
            self._status.set("환율 데이터 없음 — 네트워크 확인 후 갱신")

    def _refresh(self) -> None:
        self._status.set("환율 갱신 중…")
        box: dict = {}

        def work():
            try:
                forex.refresh()
            except Exception as exc:  # offline: keep last-known cache
                box["err"] = str(exc)

        t = threading.Thread(target=work, daemon=True)
        t.start()
        self._poll(t, box)

    def _poll(self, t: threading.Thread, box: dict) -> None:
        if t.is_alive():
            self.after(100, lambda: self._poll(t, box))
            return
        self._populate_codes()
        if "err" in box and not forex.info()[0]:
            self._status.set("오프라인 — 환율을 가져올 수 없습니다")
        elif "err" in box:
            self._status.set(
                "오프라인 — 마지막 환율 사용 중 " + f"(기준일 {forex.info()[0]})"
            )
        else:
            self._update_status()

    # --- actions --------------------------------------------------------
    def _swap(self) -> None:
        f, t = self._from.get(), self._to.get()
        self._from.set(t)
        self._to.set(f)
        self._convert()

    def _convert(self) -> None:
        frm, to = self._from.get(), self._to.get()
        if not frm or not to:
            self._result.set("환율 로딩 중…")
            return
        try:
            amount = _f(self._amount.get())
            value = forex.convert(amount, frm, to)
        except (ValueError, OSError) as e:
            self._result.set(f"오류: {e}")
            return
        text = f"{format_value(value, '천단위')} {to}"
        self._result.set(text)
        if self._on_record:
            expr = f"{amount:g} {frm} → {to}"
            self._on_record(
                expr, text, {"amount": self._amount.get(), "from": frm, "to": to}
            )

    def load(self, entry) -> None:
        inp = entry.inputs
        self._populate_codes()
        self._amount.set(str(inp.get("amount", "1")))
        if inp.get("from"):
            self._from.set(inp["from"])
        if inp.get("to"):
            self._to.set(inp["to"])
        self._convert()

    def on_key(self, event: tk.Event) -> None:
        if event.keysym in ("Return", "KP_Enter"):
            self._convert()
