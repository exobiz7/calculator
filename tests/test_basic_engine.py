from calc.modes.basic import CalculatorEngine, format_number


def feed_digits(eng, s):
    for ch in s:
        if ch == ".":
            eng.input_dot()
        else:
            eng.input_digit(ch)


def test_format_number():
    assert format_number(5.0) == "5"
    assert format_number(2.5) == "2.5"


def test_simple_addition():
    eng = CalculatorEngine()
    feed_digits(eng, "12")
    eng.set_operator("+")
    feed_digits(eng, "8")
    eng.equals()
    assert eng.display == "20"


def test_chained_operations():
    eng = CalculatorEngine()
    feed_digits(eng, "2")
    eng.set_operator("+")
    feed_digits(eng, "3")
    eng.set_operator("*")  # computes 2+3=5 first
    assert eng.display == "5"
    feed_digits(eng, "4")
    eng.equals()
    assert eng.display == "20"


def test_divide_by_zero_shows_error():
    eng = CalculatorEngine()
    feed_digits(eng, "5")
    eng.set_operator("/")
    feed_digits(eng, "0")
    eng.equals()
    assert eng.display == "Error"
    eng.input_digit("7")  # entering a digit recovers
    assert eng.display == "7"


def test_percent_with_pending_add():
    eng = CalculatorEngine()
    feed_digits(eng, "200")
    eng.set_operator("+")
    feed_digits(eng, "10")
    eng.percent()  # 10% of 200 = 20
    assert eng.display == "20"
    eng.equals()
    assert eng.display == "220"


def test_unary_square_and_sqrt():
    eng = CalculatorEngine()
    feed_digits(eng, "9")
    eng.square()
    assert eng.display == "81"
    eng.square_root()
    assert eng.display == "9"


def test_negate():
    eng = CalculatorEngine()
    feed_digits(eng, "5")
    eng.negate()
    assert eng.display == "-5"
    eng.negate()
    assert eng.display == "5"


def test_memory_and_grand_total():
    eng = CalculatorEngine()
    feed_digits(eng, "10")
    eng.memory_add()
    feed_digits(eng, "4")
    eng.memory_subtract()
    eng.memory_recall()
    assert eng.display == "6"

    eng.all_clear()
    feed_digits(eng, "2")
    eng.set_operator("+")
    feed_digits(eng, "3")
    eng.equals()  # 5 -> GT
    feed_digits(eng, "1")
    eng.set_operator("+")
    feed_digits(eng, "1")
    eng.equals()  # 2 -> GT
    assert eng.grand_total.total == 7
