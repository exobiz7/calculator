from calc.core.history import HistoryEntry, HistoryStore


def test_add_and_recent(tmp_path):
    store = HistoryStore(path=tmp_path / "h.json")
    store.record("기본", "2 + 3", "5")
    store.record("공학용", "sqrt(2)", "1.414")
    recent = store.recent()
    assert [e.expression for e in recent] == ["sqrt(2)", "2 + 3"]  # newest first
    assert recent[0].mode == "공학용"


def test_recent_limit(tmp_path):
    store = HistoryStore(path=tmp_path / "h.json")
    for i in range(5):
        store.record("기본", f"{i}+0", str(i))
    assert len(store.recent(3)) == 3


def test_persistence_roundtrip(tmp_path):
    p = tmp_path / "h.json"
    s1 = HistoryStore(path=p)
    s1.record(
        "경영지표",
        "net_income/equity*100",
        "20",
        inputs={"net_income": 100, "equity": 500},
    )
    # New store instance reads the same file
    s2 = HistoryStore(path=p)
    e = s2.recent()[0]
    assert e.expression == "net_income/equity*100"
    assert e.result == "20"
    assert e.inputs == {"net_income": 100, "equity": 500}


def test_cap_enforced(tmp_path):
    store = HistoryStore(path=tmp_path / "h.json", max_entries=10)
    for i in range(25):
        store.record("기본", f"{i}+0", str(i))
    entries = store.recent()
    assert len(entries) == 10
    assert entries[0].result == "24"  # newest kept


def test_clear(tmp_path):
    store = HistoryStore(path=tmp_path / "h.json")
    store.record("기본", "1+1", "2")
    store.clear()
    assert store.recent() == []


def test_corrupt_file_starts_empty(tmp_path):
    p = tmp_path / "h.json"
    p.write_text("{not valid json", encoding="utf-8")
    store = HistoryStore(path=p)
    assert store.recent() == []
    store.record("기본", "1+1", "2")  # still usable
    assert len(store.recent()) == 1


def test_entry_has_timestamp():
    e = HistoryEntry(mode="기본", expression="1+1", result="2")
    assert e.timestamp  # auto-populated ISO string
