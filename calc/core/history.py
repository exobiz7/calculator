"""Calculation history with JSON persistence.

Records each calculation as a reusable entry (expression/formula + inputs +
result) so the UI can both re-run a result and re-use the formula itself.
Stored outside the repo at ~/.calculator/history.json.
"""

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

MAX_ENTRIES = 200


@dataclass
class HistoryEntry:
    mode: str  # "기본" / "공학용" / "경영지표" / ...
    expression: str  # reusable expression or formula
    result: str
    inputs: dict = field(default_factory=dict)  # variable values (KPI/AI)
    timestamp: str = field(
        default_factory=lambda: datetime.now().isoformat(timespec="seconds")
    )


def _default_path() -> Path:
    return Path.home() / ".calculator" / "history.json"


class HistoryStore:
    """Append-only (capped) calculation history, persisted to JSON."""

    def __init__(
        self, path: Path | None = None, max_entries: int = MAX_ENTRIES
    ) -> None:
        self.path = Path(path) if path is not None else _default_path()
        self.max_entries = max_entries
        self._entries: list[HistoryEntry] = self._load()

    # --- public API -----------------------------------------------------
    def add(self, entry: HistoryEntry) -> None:
        self._entries.append(entry)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]
        self._save()

    def record(
        self, mode: str, expression: str, result: str, inputs: dict | None = None
    ) -> None:
        """Convenience wrapper used by the UI callback."""
        self.add(
            HistoryEntry(
                mode=mode, expression=expression, result=result, inputs=inputs or {}
            )
        )

    def recent(self, n: int | None = None) -> list[HistoryEntry]:
        """Most-recent-first list (optionally limited to n)."""
        items = list(reversed(self._entries))
        return items[:n] if n is not None else items

    def clear(self) -> None:
        self._entries = []
        self._save()

    # --- persistence ----------------------------------------------------
    def _load(self) -> list[HistoryEntry]:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return [HistoryEntry(**item) for item in raw][-self.max_entries :]
        except (FileNotFoundError, ValueError, TypeError):
            return []  # missing or corrupt → start empty

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(
                    [asdict(e) for e in self._entries], ensure_ascii=False, indent=2
                ),
                encoding="utf-8",
            )
        except OSError:
            pass  # never let a failed write crash a calculation
