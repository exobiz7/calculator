"""Entry point: a tiny interactive calculator."""

from calculator import calculate


def main() -> None:
    print("Simple Calculator (operators: + - * /, type 'q' to quit)")
    while True:
        expr = input("> ").strip()
        if expr.lower() in {"q", "quit", "exit"}:
            print("Bye!")
            break
        try:
            a_str, op, b_str = expr.split()
            result = calculate(float(a_str), op, float(b_str))
            print(f"= {result}")
        except ValueError as e:
            print(f"Error: {e}")
        except Exception:
            print("Invalid input. Example: 3 + 4")


if __name__ == "__main__":
    main()
