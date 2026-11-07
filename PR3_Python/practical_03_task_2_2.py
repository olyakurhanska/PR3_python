
"""Декоратори класів."""

import functools
import inspect
import time


def auto_repr(cls):
    """Автоматично додає __repr__ на основі параметрів __init__."""
    parameters = [
        name
        for name in inspect.signature(cls.__init__).parameters
        if name != "self"
    ]

    def __repr__(self):
        attributes = ", ".join(
            f"{name}={getattr(self, name)!r}"
            for name in parameters
        )
        return f"{cls.__name__}({attributes})"

    cls.__repr__ = __repr__
    return cls


def frozen(cls):
    """Забороняє зміну атрибутів після ініціалізації."""
    original_init = cls.__init__
    original_setattr = cls.__setattr__

    @functools.wraps(original_init)
    def new_init(self, *args, **kwargs):
        original_setattr(self, "_frozen", False)
        original_init(self, *args, **kwargs)
        original_setattr(self, "_frozen", True)

    def new_setattr(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(
                f"Не можна змінювати атрибут '{name}': об'єкт заморожено"
            )
        original_setattr(self, name, value)

    cls.__init__ = new_init
    cls.__setattr__ = new_setattr
    return cls


def log_methods(cls):
    """Логує виклики всіх публічних методів класу."""

    def create_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            print(f"[LOG] Виклик {method.__name__}")
            start = time.perf_counter()

            try:
                result = method(self, *args, **kwargs)
                elapsed = time.perf_counter() - start
                print(
                    f"[LOG] {method.__name__} -> {result} "
                    f"(час: {elapsed:.4f}с)"
                )
                return result
            except Exception as error:
                print(f"[ERROR] {method.__name__}: {error}")
                raise

        return wrapper

    for name, method in vars(cls).copy().items():
        if not name.startswith("_") and inspect.isfunction(method):
            setattr(cls, name, create_wrapper(method))

    return cls


@auto_repr
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: "Point") -> float:
        return (
            (self.x - other.x) ** 2
            + (self.y - other.y) ** 2
        ) ** 0.5


@frozen
class ImmutableConfig:
    def __init__(
        self, host: str, port: int, debug: bool = False
    ):
        self.host = host
        self.port = port
        self.debug = debug


@log_methods
class MathService:
    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Ділення на нуль")
        return a / b


@auto_repr
@frozen
@log_methods
class CombinedExample:
    """Демонстрація поєднання трьох декораторів."""

    def __init__(self, value: int):
        self.value = value

    def double(self):
        return self.value * 2


def main():
    print("=== 1. Декоратор auto_repr ===")
    point = Point(3.0, 4.0)
    print(repr(point))
    print("Відстань до (0, 0):", point.distance_to(Point(0, 0)))

    print("\n=== 2. Декоратор frozen ===")
    cfg = ImmutableConfig("localhost", 8080, debug=True)
    print(f"Config: {cfg.host}:{cfg.port}")

    try:
        cfg.host = "remote"
    except AttributeError as error:
        print(f"Очікувана помилка: {error}")

    print("\n=== 3. Декоратор log_methods ===")
    svc = MathService()
    svc.add(10, 20)
    svc.multiply(3, 7)

    try:
        svc.divide(10, 0)
    except ValueError:
        print("Помилку ValueError успішно оброблено")

    print("\n=== 4. Комбінування декораторів ===")
    example = CombinedExample(5)
    print(repr(example))
    print("Подвоєне значення:", example.double())

    try:
        example.value = 10
    except AttributeError as error:
        print(f"Очікувана помилка: {error}")


if __name__ == "__main__":
    main()
