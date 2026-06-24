
from calc.modes.scientific import ScientificEngine


def test_build_and_evaluate():
    eng = ScientificEngine()
    for tok in ["2", "+", "3", "*", "4"]:
        eng.insert(tok)
    assert eng.evaluate() == "14"
    assert eng.last_answer == 14


def test_angle_toggle_affects_result():
    eng = ScientificEngine()
    eng.insert("sin(30)")
    assert eng.evaluate() != "0.5"  # default RAD
    eng.clear()
    eng.toggle_angle()  # -> DEG
    eng.insert("sin(30)")
    assert eng.evaluate() == "0.5"


def test_error_recovers_on_next_insert():
    eng = ScientificEngine()
    eng.insert("1/0")
    assert eng.evaluate() == "Error"
    eng.insert("5")  # error state clears, expression resets
    assert eng.expression == "5"


def test_use_answer():
    eng = ScientificEngine()
    eng.insert("10")
    eng.evaluate()
    eng.clear()
    eng.use_answer()
    eng.insert("+5")
    assert eng.evaluate() == "15"
