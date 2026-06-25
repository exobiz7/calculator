"""Tkinter view for the AI calculator mode (multi-provider, user-configured)."""

import threading
import tkinter as tk
from tkinter import filedialog

import ttkbootstrap as ttk

from calc.core import ai_config, ai_formula
from calc.core.expr import safe_eval
from calc.core.numfmt import format_value

_TIMEOUT = 40


def _to_float(text: str, default: float = 0.0) -> float:
    text = text.replace(",", "").strip()
    return float(text) if text else default


class AIView(ttk.Frame):
    def __init__(self, master: tk.Misc, on_record=None) -> None:
        super().__init__(master, padding=10)
        self._on_record = on_record
        self._config = ai_config.load()
        self._image: bytes | None = None
        self._formula: ai_formula.AIFormula | None = None
        self._var_entries: dict[str, tk.StringVar] = {}
        self._status = tk.StringVar(value="")
        self._expr_var = tk.StringVar(value="")
        self._result = tk.StringVar(value="")
        self._img_var = tk.StringVar(value="이미지 없음")
        self._build()

    # --- layout ---------------------------------------------------------
    def _build(self) -> None:
        ttk.Label(self, text="모델 설정", font=("Helvetica", 11, "bold")).pack(
            anchor="w"
        )
        cfg = ttk.Frame(self, padding=(0, 4))
        cfg.pack(fill="x")
        self._preset = ttk.Combobox(
            cfg, values=list(ai_config.PRESETS), state="readonly", width=18
        )
        self._preset.set(self._config.preset)
        self._preset.grid(row=0, column=0, columnspan=2, sticky="w", pady=2)
        self._preset.bind("<<ComboboxSelected>>", lambda e: self._apply_preset())
        self._base = self._labeled(cfg, "base_url", 1, self._config.base_url)
        self._model = self._labeled(cfg, "model", 2, self._config.model)
        ttk.Label(cfg, text="API 키").grid(row=3, column=0, sticky="w", pady=2)
        self._key = tk.StringVar(value=self._config.api_key)
        self._key_entry = ttk.Entry(cfg, textvariable=self._key, show="•", width=28)
        self._key_entry.grid(row=3, column=1, sticky="we", pady=2)
        ttk.Button(
            cfg,
            text="👁",
            width=3,
            bootstyle="secondary-outline",
            command=self._toggle_key,
        ).grid(row=3, column=2, padx=2)
        ttk.Button(cfg, text="저장", bootstyle="secondary", command=self._save).grid(
            row=4, column=0, sticky="we", pady=(4, 0)
        )
        ttk.Button(
            cfg, text="연결 테스트", bootstyle="info-outline", command=self._test
        ).grid(row=4, column=1, sticky="we", pady=(4, 0))
        cfg.columnconfigure(1, weight=1)

        inp = ttk.Frame(self, padding=(0, 8))
        inp.pack(fill="x")
        ttk.Label(inp, text="요청 (자연어 / 공식 / LaTeX)").pack(anchor="w")
        self._prompt = tk.Text(inp, height=3)
        self._prompt.pack(fill="x")
        imgrow = ttk.Frame(inp)
        imgrow.pack(fill="x", pady=(4, 0))
        ttk.Button(
            imgrow,
            text="이미지 선택",
            bootstyle="secondary-outline",
            command=self._pick_image,
        ).pack(side="left")
        ttk.Button(
            imgrow,
            text="✕",
            width=3,
            bootstyle="secondary-outline",
            command=self._clear_image,
        ).pack(side="left", padx=(2, 6))
        ttk.Label(imgrow, textvariable=self._img_var, bootstyle="secondary").pack(
            side="left"
        )

        ttk.Button(
            self, text="공식 생성", bootstyle="primary", command=self._generate
        ).pack(fill="x", pady=4)
        ttk.Label(
            self,
            textvariable=self._expr_var,
            bootstyle="info",
            font=("Helvetica", 13),
            wraplength=380,
        ).pack(anchor="w")

        self._vframe = ttk.Frame(self)
        self._vframe.pack(fill="x")
        self._calc_btn = ttk.Button(
            self, text="계산", bootstyle="success", command=self._calc, state="disabled"
        )
        self._calc_btn.pack(fill="x", pady=4)
        ttk.Label(
            self,
            textvariable=self._result,
            bootstyle="success",
            font=("Helvetica", 20, "bold"),
        ).pack(anchor="w")
        ttk.Label(
            self, textvariable=self._status, bootstyle="secondary", wraplength=380
        ).pack(anchor="w")

    def _labeled(self, parent, label, row, value):
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=2)
        sv = tk.StringVar(value=value)
        ttk.Entry(parent, textvariable=sv, width=28).grid(
            row=row, column=1, columnspan=2, sticky="we", pady=2
        )
        return sv

    # --- settings -------------------------------------------------------
    def _apply_preset(self) -> None:
        c = ai_config.from_preset(self._preset.get())
        self._base.set(c.base_url)
        self._model.set(c.model)

    def _toggle_key(self) -> None:
        self._key_entry.configure(show="" if self._key_entry.cget("show") else "•")

    def _current_config(self) -> ai_config.AIConfig:
        preset = self._preset.get()
        kind = ai_config.PRESETS.get(preset, {}).get("kind", "openai")
        return ai_config.AIConfig(
            preset=preset,
            kind=kind,
            base_url=self._base.get(),
            model=self._model.get(),
            api_key=self._key.get(),
        )

    def _save(self) -> None:
        self._config = self._current_config()
        ai_config.save(self._config)
        self._status.set("설정 저장됨 (~/.calculator/ai_config.json, 권한 600)")

    def _test(self) -> None:
        self._run_async(
            "연결 테스트 중…",
            lambda cfg: ai_formula.request_formula(cfg, "1+1", timeout=_TIMEOUT),
            lambda f: self._status.set("연결 성공 ✓"),
        )

    # --- image ----------------------------------------------------------
    def _pick_image(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[
                ("이미지", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("모든 파일", "*.*"),
            ]
        )
        if not path:
            return
        try:
            data = open(path, "rb").read()
        except OSError as e:
            self._status.set(f"이미지 읽기 실패: {e}")
            return
        if len(data) > 8 * 1024 * 1024:
            self._status.set("이미지가 너무 큽니다 (8MB 이하)")
            return
        self._image = data
        self._img_var.set(path.rsplit("/", 1)[-1])

    def _clear_image(self) -> None:
        self._image = None
        self._img_var.set("이미지 없음")

    # --- generate (threaded) -------------------------------------------
    def _generate(self) -> None:
        prompt = self._prompt.get("1.0", "end").strip()
        image = self._image
        self._run_async(
            "공식 생성 중…",
            lambda cfg: ai_formula.request_formula(
                cfg, prompt, image, timeout=_TIMEOUT
            ),
            self._on_formula,
        )

    def _run_async(self, busy_msg, work_fn, done_fn) -> None:
        cfg = self._current_config()
        if not cfg.model:
            self._status.set("model을 입력하세요")
            return
        if cfg.kind != "openai" or "localhost" not in cfg.base_url:
            if not cfg.effective_key():
                self._status.set("API 키가 필요합니다 (저장 또는 환경변수)")
                return
        self._status.set(busy_msg)
        box: dict = {}

        def work():
            try:
                box["ok"] = work_fn(cfg)
            except Exception as exc:
                box["err"] = str(exc)

        t = threading.Thread(target=work, daemon=True)
        t.start()
        self._poll(t, box, done_fn)

    def _poll(self, t, box, done_fn) -> None:
        if t.is_alive():
            self.after(120, lambda: self._poll(t, box, done_fn))
            return
        if "err" in box:
            self._status.set(f"오류: {box['err']}")
            return
        self._status.set("")
        done_fn(box["ok"])

    def _on_formula(self, formula: ai_formula.AIFormula) -> None:
        self._formula = formula
        self._expr_var.set(
            f"식: {formula.expression}"
            + (f"\n{formula.explanation}" if formula.explanation else "")
        )
        self._render_vars(formula.variables)
        self._calc_btn.configure(state="normal")

    def _render_vars(self, variables) -> None:
        for w in self._vframe.winfo_children():
            w.destroy()
        self._var_entries = {}
        for r, v in enumerate(variables):
            ttk.Label(self._vframe, text=v.get("label", v["name"])).grid(
                row=r, column=0, sticky="w", pady=2
            )
            sv = tk.StringVar()
            ttk.Entry(self._vframe, textvariable=sv, width=16).grid(
                row=r, column=1, sticky="we", pady=2, padx=(8, 0)
            )
            self._var_entries[v["name"]] = sv
        self._vframe.columnconfigure(1, weight=1)

    # --- evaluate -------------------------------------------------------
    def _calc(self) -> None:
        if not self._formula:
            return
        try:
            values = {n: _to_float(sv.get()) for n, sv in self._var_entries.items()}
            value = safe_eval(self._formula.expression, variables=values)
        except (ValueError, ZeroDivisionError, OverflowError) as e:
            self._result.set(f"오류: {e}")
            return
        text = format_value(float(value))
        self._result.set(text)
        if self._on_record:
            self._on_record(
                self._formula.expression,
                text,
                {
                    "expr": self._formula.expression,
                    "prompt": self._prompt.get("1.0", "end").strip(),
                    "vars": {n: sv.get() for n, sv in self._var_entries.items()},
                },
            )

    def load(self, entry) -> None:
        inp = entry.inputs
        expr = inp.get("expr", "")
        if not expr:
            return
        vals = inp.get("vars", {})
        self._formula = ai_formula.AIFormula(
            expr, [{"name": n, "label": n} for n in vals]
        )
        self._prompt.delete("1.0", "end")
        self._prompt.insert("1.0", inp.get("prompt", ""))
        self._expr_var.set(f"식: {expr}")
        self._render_vars(self._formula.variables)
        for n, sv in self._var_entries.items():
            sv.set(str(vals.get(n, "")))
        self._calc_btn.configure(state="normal")
        self._calc()

    def on_key(self, event: tk.Event) -> None:
        return
